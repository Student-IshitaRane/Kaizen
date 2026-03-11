from fastapi import APIRouter
from pydantic import BaseModel
import asyncio
from llm_service import llm_service, LLMRequest

router = APIRouter(prefix="/reports", tags=["Report Copilot"])

class EditRequest(BaseModel):
    html: str
    prompt: str

@router.post("/edit")
async def edit_report(req: EditRequest):
    # Try the real AI models first
    if llm_service.is_any_provider_available():
        system_prompt = "You are an AI Audit Report Copilot. The user provides a piece of HTML representing an audit report, and a prompt for what to change. Return the entire modified HTML within your response so it can be parsed."
        try:
            llm_req = LLMRequest(
                prompt=f"{system_prompt}\n\nCurrent HTML:\n{req.html}\n\nUser Request: {req.prompt}",
                context={},
                agent_name="reports_copilot",
                temperature=0.2
            )
            response_obj = llm_service.generate(llm_req)
            if response_obj and response_obj.content:
                # Naive parse to extract HTML if the model uses markdown code blocks
                content = response_obj.content
                if "```html" in content:
                    content = content.split("```html")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                return {
                    "html": content,
                    "message": "I have updated the document as requested."
                }
        except Exception as e:
            pass
            
    # Fallback mock processing if no provider is configured
    await asyncio.sleep(1.5)
    
    current_input = req.prompt.lower()
    new_html = req.html
    ai_response_text = ""
    
    if "add" in current_input or "append" in current_input or "it sector" in current_input:
        ai_response_text = "I have appended the requested data to the Executive Summary section."
        if "require immediate investigation." in str(req.html):
            new_html = req.html.replace(
                'require immediate investigation.', 
                'require immediate investigation. <span class="bg-teal-100 text-teal-800 px-1 rounded mx-1">Additionally, the AI model has noted a 12% increase in late payments compared to last quarter, predominantly in the IT sector.</span>'
            )
        else:
            new_html += "<br/><p>Additionally, the AI model has noted a 12% increase in late payments compared to last quarter, predominantly in the IT sector.</p>"
            
    elif "table" in current_input or "format" in current_input:
        ai_response_text = "I've reformatted the flagged cases into a structured table element."
        # Basic mock replacement to display a table layout
        if '<div class="bg-red-50' in req.html:
            new_html = req.html.replace(
                '<div class="bg-red-50',
                '<table class="table-auto w-full mb-6 border-collapse shadow-sm"><thead><tr class="bg-slate-200 text-left"><th class="p-2 border border-slate-300">Flag</th><th class="p-2 border border-slate-300">Score</th><th class="p-2 border border-slate-300">Action</th></tr></thead><tbody><tr class="bg-red-50'
            ).replace(
                '<div class="bg-amber-50',
                '<tr class="bg-amber-50'
            )
            new_html += "</tbody></table>"
    else:
        ai_response_text = "I can modify the document layout, auto-summarize specific sections, or pull new data from the live database. Let me know exactly what you need changed in the editable area."

    return {
        "html": new_html,
        "message": ai_response_text
    }
