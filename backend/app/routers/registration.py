"""Garment registration: activation (I1) and QR scan (I5)."""
from __future__ import annotations

import html

import qrcode
import qrcode.image.svg
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session

from .. import registration, services
from ..deps import current_user, get_session, require_api_key
from ..models import GarmentCode
from ..schemas import ActivateIn, GarmentOut

router = APIRouter(tags=["registration"])
gs1_router = APIRouter(tags=["registration"])  # mounted at the site root: https://host/01/{gtin}/21/{serial}


@router.post("/garments/activate", status_code=201, response_model=GarmentOut, dependencies=[Depends(require_api_key)])
def activate(body: ActivateIn, s: Session = Depends(get_session), user=Depends(current_user)):
    """Redeem the private activation code. 400 with one generic message for every kind of
    bad input; 429 after 10 attempts in an hour."""
    try:
        g = registration.activate(s, user, body.code)
    except registration.RateLimited:
        return JSONResponse(status_code=429, content={"detail": "too many attempts, try again later"})
    except registration.ActivationError:
        return JSONResponse(status_code=400, content={"detail": registration.GENERIC_ERROR})
    return services.garment_out(g)


def _page_or_404(s: Session, request: Request, gtin: str, serial: str) -> dict:
    page = registration.product_page(s, gtin, serial, str(request.base_url))
    if page is None:
        raise HTTPException(status_code=404, detail="unknown product tag")
    return page


@router.get("/scan/01/{gtin}/21/{serial}")
def scan(gtin: str, serial: str, request: Request, s: Session = Depends(get_session)):
    """I5 resolver (JSON). Shows the product only; never grants ownership."""
    return _page_or_404(s, request, gtin, serial)


@gs1_router.get("/01/{gtin}/21/{serial}", response_class=HTMLResponse, include_in_schema=True)
def scan_page(gtin: str, serial: str, request: Request, s: Session = Depends(get_session)):
    """What the phone camera opens: the GS1 Digital Link printed in the tag's QR code."""
    p = _page_or_404(s, request, gtin, serial)
    e = html.escape
    return (
        "<!doctype html><meta name=viewport content='width=device-width'><title>Product</title>"
        f"<h1>{e(p['name'])}</h1><p>Category: {e(p['category'])} · slot: {e(p['slot'])} · "
        f"colour <span style='background:{e(p['color_hex'])}'>&nbsp;&nbsp;&nbsp;</span></p>"
        f"<p>GTIN {e(p['gtin'])}</p><p><b>Wishlist only.</b> {e(p['ownership'])}</p>"
    )


@router.get("/codes/{serial}/qr.svg", dependencies=[Depends(require_api_key)])
def qr_svg(serial: str, request: Request, s: Session = Depends(get_session)):
    """QR image of the tag's public Digital Link (for printing demo tags)."""
    code = s.get(GarmentCode, serial)
    if code is None:
        raise HTTPException(status_code=404, detail="unknown serial")
    url = f"{str(request.base_url).rstrip('/')}/01/{code.gtin}/21/{serial}"
    img = qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage)
    return Response(content=img.to_string(), media_type="image/svg+xml")
