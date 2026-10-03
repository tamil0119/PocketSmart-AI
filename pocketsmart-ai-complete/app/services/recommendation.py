import json
from io import BytesIO
from typing import Any
from PIL import Image
from ..config import get_settings
from .catalog import search_url

settings = get_settings()

def _money(v: float) -> float:
    return round(max(0.0, float(v)), 2)

def _fallback_home(data: dict[str, Any]) -> dict[str, Any]:
    b = float(data["budget"]); room=data["room_type"]; style=data.get("style","modern")
    specs=[("Lighting","LED/ambient lighting",0.18,"Amazon"),("Ceiling fan","Energy-efficient fan",0.20,"Flipkart"),("Furniture","Compact table/storage",0.34,"IKEA"),("Decor","Wall art/soft furnishings",0.18,"Amazon")]
    items=[]
    for cat,name,pct,platform in specs:
        price=_money(b*pct)
        items.append({"name":f"{style.title()} {name}","category":cat,"estimated_price":price,"platform":platform,"reason":f"Balanced choice for a {style} {room} while preserving budget reserve.","search_url":search_url(platform,f"{style} {room} {name}")})
    total=sum(x["estimated_price"] for x in items)
    return {"planner":"home","budget":b,"estimated_total":_money(total),"summary":f"A practical {style} setup for your {room} with a reserve for delivery or price variation.","items":items,"tips":["Compare final prices and delivery charges before purchase.","Keep 5–10% of the budget unallocated for price changes."],"source":"fallback"}

def _fallback_party(data: dict[str, Any]) -> dict[str, Any]:
    b=float(data["budget"]); guests=int(data["guests"]); event=data["event_type"]
    specs=[("Catering",0.48,"Swiggy"),("Venue",0.25,"OYO"),("Decoration",0.17,"Amazon"),("Entertainment",0.10,"Flipkart")]
    items=[]
    for cat,pct,platform in specs:
        price=_money(b*pct); query=f"{event} {cat} {data.get('city','')}"
        items.append({"name":f"{event.title()} {cat} allocation","category":cat,"estimated_price":price,"platform":platform,"reason":f"Planned for about {guests} guests with a proportional budget split.","search_url":search_url(platform,query)})
    return {"planner":"party","budget":b,"estimated_total":_money(sum(i["estimated_price"] for i in items)),"summary":f"Budget allocation for a {event} with {guests} guests.","items":items,"tips":[f"Target food cost near ₹{_money(b*0.48/guests)} per guest within this plan.","Confirm vendor minimum order values and venue taxes."],"source":"fallback"}

def _fallback_jewelry(data: dict[str, Any], image_note: str="") -> dict[str, Any]:
    b=float(data["budget"]); occ=data["occasion"]; style=data.get("style","elegant"); color=data.get("outfit_color","")
    specs=[("Necklace",0.45,"Amazon"),("Earrings",0.28,"Flipkart"),("Bracelet/Bangles",0.20,"Amazon")]
    items=[]
    for cat,pct,platform in specs:
        query=f"{style} {occ} {color} {cat} jewelry"
        items.append({"name":f"{style.title()} {cat}","category":cat,"estimated_price":_money(b*pct),"platform":platform,"reason":f"Selected to suit a {occ} look{(' with '+color+' tones') if color else ''}.","search_url":search_url(platform,query)})
    summary=f"A coordinated {style} jewelry set for {occ}."
    if image_note: summary += " Outfit image was considered by the planner."
    return {"planner":"jewelry","budget":b,"estimated_total":_money(sum(i["estimated_price"] for i in items)),"summary":summary,"items":items,"tips":["Verify material, dimensions, seller rating, and return policy.","Use the platform links as searches; displayed prices are estimates."],"source":"fallback"}

def _schema() -> dict:
    return {"type":"object","properties":{"summary":{"type":"string"},"items":{"type":"array","items":{"type":"object","properties":{"name":{"type":"string"},"category":{"type":"string"},"estimated_price":{"type":"number"},"platform":{"type":"string"},"reason":{"type":"string"}},"required":["name","category","estimated_price","platform","reason"]}},"tips":{"type":"array","items":{"type":"string"}}},"required":["summary","items","tips"]}

def _ask_gemini(planner: str, data: dict[str, Any], image_bytes: bytes|None=None, mime_type: str|None=None) -> dict[str, Any] | None:
    if not settings.use_gemini or not settings.gemini_api_key:
        return None
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return None
    client=genai.Client(api_key=settings.gemini_api_key)
    prompt=("You are PocketSmart AI, a budget recommendation assistant for India. "
            "Return realistic category-level recommendations, not claims of live prices or inventory. "
            "Never exceed the user's total budget. Allowed platforms: Amazon, Flipkart, IKEA, Swiggy, Zomato, OYO. "
            f"Planner: {planner}. User input: {json.dumps(data, ensure_ascii=False)}")
    contents: list[Any]=[prompt]
    if image_bytes:
        contents.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type or "image/jpeg"))
    try:
        response=client.models.generate_content(model=settings.gemini_model, contents=contents, config=types.GenerateContentConfig(response_mime_type="application/json", response_json_schema=_schema(), temperature=0.3))
        parsed=json.loads(response.text or "{}")
        items=[]; budget=float(data["budget"]); running=0.0
        for raw in parsed.get("items",[])[:8]:
            price=_money(raw.get("estimated_price",0))
            if price <= 0 or running + price > budget: continue
            platform=raw.get("platform","Amazon")
            item={**raw,"estimated_price":price,"platform":platform,"search_url":search_url(platform,raw.get("name","product"))}
            items.append(item); running += price
        if not items: return None
        return {"planner":planner,"budget":budget,"estimated_total":_money(running),"summary":parsed.get("summary","AI-generated budget plan."),"items":items,"tips":parsed.get("tips",[])[:5],"source":"gemini"}
    except Exception:
        return None

def home_recommendations(data: dict[str, Any]) -> dict[str, Any]:
    return _ask_gemini("home",data) or _fallback_home(data)

def party_recommendations(data: dict[str, Any]) -> dict[str, Any]:
    return _ask_gemini("party",data) or _fallback_party(data)

def jewelry_recommendations(data: dict[str, Any], image_bytes: bytes|None=None, mime_type: str|None=None) -> dict[str, Any]:
    result=_ask_gemini("jewelry",data,image_bytes,mime_type)
    return result or _fallback_jewelry(data,"uploaded" if image_bytes else "")
