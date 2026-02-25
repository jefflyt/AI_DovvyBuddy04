"""Email template builders for lead notifications."""

from typing import Any, Dict

from app.core.lead.types import LeadRecord


def build_lead_email_subject(lead: LeadRecord) -> str:
    """Build email subject line for lead notification.
    
    Args:
        lead: Lead record to format
        
    Returns:
        Formatted subject line with lead type, name, and ID prefix
    """
    lead_id_prefix = str(lead.id)[:8]
    name = lead.request_details.get("name", "Unknown")
    return f"[DovvyBuddy] New {lead.type} Lead: {name} [{lead_id_prefix}]"


def build_lead_email_html(lead: LeadRecord) -> str:
    """Build HTML email content for lead notification.
    
    Args:
        lead: Lead record to format
        
    Returns:
        Formatted HTML email with all lead details
    """
    request_details = lead.request_details
    diver_profile = lead.diver_profile or {}
    
    # Lead type display name
    lead_type_display = "Training Inquiry" if lead.type == "training" else "Trip Planning Request"
    
    # Build contact information section
    contact_html = f"""
        <p><strong>Name:</strong> {request_details.get('name', 'N/A')}</p>
        <p><strong>Email:</strong> <a href="mailto:{request_details.get('email', '')}">{request_details.get('email', 'N/A')}</a></p>
    """
    
    if request_details.get('phone'):
        contact_html += f"""<p><strong>Phone:</strong> {request_details['phone']}</p>"""
    
    # Build request details section based on lead type
    if lead.type == "training":
        details_html = ""
        if request_details.get('certification_level'):
            details_html += f"""<p><strong>Current Certification:</strong> {request_details['certification_level']}</p>"""
        if request_details.get('interested_certification'):
            details_html += f"""<p><strong>Interested In:</strong> {request_details['interested_certification']}</p>"""
        if request_details.get('preferred_location'):
            details_html += f"""<p><strong>Preferred Location:</strong> {request_details['preferred_location']}</p>"""
    else:  # trip
        details_html = ""
        if request_details.get('destination'):
            details_html += f"""<p><strong>Destination:</strong> {request_details['destination']}</p>"""
        if request_details.get('travel_dates'):
            details_html += f"""<p><strong>Travel Dates:</strong> {request_details['travel_dates']}</p>"""
        if request_details.get('group_size'):
            details_html += f"""<p><strong>Group Size:</strong> {request_details['group_size']} travelers</p>"""
        if request_details.get('budget'):
            details_html += f"""<p><strong>Budget:</strong> {request_details['budget']}</p>"""
    
    # Add message if present
    message_html = ""
    if request_details.get('message'):
        message_html = f"""
        <div style="background-color: #f5f5f5; padding: 15px; border-left: 4px solid #0066cc; margin: 15px 0;">
            <p style="margin: 0;"><strong>Message:</strong></p>
            <p style="margin: 10px 0 0 0; white-space: pre-wrap;">{request_details['message']}</p>
        </div>
        """
    
    # Build diver profile section if available
    profile_html = ""
    if diver_profile:
        profile_html = """
        <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin-top: 20px;">
            <h3 style="color: #0066cc; margin-top: 0;">Diver Profile (from session)</h3>
        """
        if diver_profile.get('certification_level'):
            profile_html += f"""<p><strong>Certification Level:</strong> {diver_profile['certification_level']}</p>"""
        if diver_profile.get('experience_dives'):
            profile_html += f"""<p><strong>Experience:</strong> {diver_profile['experience_dives']} dives</p>"""
        if diver_profile.get('interests'):
            interests = ', '.join(diver_profile['interests'])
            profile_html += f"""<p><strong>Interests:</strong> {interests}</p>"""
        if diver_profile.get('fears'):
            fears = ', '.join(diver_profile['fears'])
            profile_html += f"""<p><strong>Concerns:</strong> {fears}</p>"""
        profile_html += """</div>"""
    
    # Assemble complete HTML email
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>New Lead from DovvyBuddy</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background-color: #0066cc; color: white; padding: 20px; border-radius: 5px 5px 0 0;">
        <h1 style="margin: 0; font-size: 24px;">New Lead from DovvyBuddy</h1>
        <p style="margin: 5px 0 0 0; font-size: 14px;">Lead ID: {lead.id}</p>
    </div>
    
    <div style="border: 1px solid #ddd; border-top: none; padding: 20px; border-radius: 0 0 5px 5px;">
        <h2 style="color: #0066cc; margin-top: 0;">{lead_type_display}</h2>
        <p style="color: #666; font-size: 14px;">Received: {lead.created_at.strftime('%B %d, %Y at %H:%M UTC')}</p>
        
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
        
        <h3 style="color: #0066cc;">Contact Information</h3>
        {contact_html}
        
        <h3 style="color: #0066cc; margin-top: 20px;">Request Details</h3>
        {details_html}
        
        {message_html}
        
        {profile_html}
        
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
        
        <div style="background-color: #e8f4f8; padding: 15px; border-radius: 5px;">
            <p style="margin: 0; font-size: 14px;"><strong>Next Steps:</strong></p>
            <p style="margin: 10px 0 0 0; font-size: 14px;">
                Reply directly to this email to contact {request_details.get('name', 'the inquirer')} 
                at <a href="mailto:{request_details.get('email', '')}">{request_details.get('email', 'N/A')}</a>
            </p>
        </div>
    </div>
    
    <div style="text-align: center; margin-top: 20px; padding: 20px; color: #666; font-size: 12px;">
        <p>This lead was generated by DovvyBuddy, your AI diving assistant</p>
        <p style="margin: 5px 0;">Lead Reference: {lead.id}</p>
    </div>
</body>
</html>
    """
    
    return html.strip()


def build_lead_email_text(lead: LeadRecord) -> str:
    """Build plain text email content for lead notification.
    
    Args:
        lead: Lead record to format
        
    Returns:
        Formatted plain text email with all lead details
    """
    request_details = lead.request_details
    diver_profile = lead.diver_profile or {}
    
    # Lead type display name
    lead_type_display = "Training Inquiry" if lead.type == "training" else "Trip Planning Request"
    
    # Build text sections
    text_parts = [
        "=" * 60,
        "NEW LEAD FROM DOVVYBUDDY",
        "=" * 60,
        f"Lead ID: {lead.id}",
        f"Type: {lead_type_display}",
        f"Received: {lead.created_at.strftime('%B %d, %Y at %H:%M UTC')}",
        "",
        "CONTACT INFORMATION",
        "-" * 60,
        f"Name: {request_details.get('name', 'N/A')}",
        f"Email: {request_details.get('email', 'N/A')}",
    ]
    
    if request_details.get('phone'):
        text_parts.append(f"Phone: {request_details['phone']}")
    
    text_parts.extend(["", "REQUEST DETAILS", "-" * 60])
    
    # Add type-specific details
    if lead.type == "training":
        if request_details.get('certification_level'):
            text_parts.append(f"Current Certification: {request_details['certification_level']}")
        if request_details.get('interested_certification'):
            text_parts.append(f"Interested In: {request_details['interested_certification']}")
        if request_details.get('preferred_location'):
            text_parts.append(f"Preferred Location: {request_details['preferred_location']}")
    else:  # trip
        if request_details.get('destination'):
            text_parts.append(f"Destination: {request_details['destination']}")
        if request_details.get('travel_dates'):
            text_parts.append(f"Travel Dates: {request_details['travel_dates']}")
        if request_details.get('group_size'):
            text_parts.append(f"Group Size: {request_details['group_size']} travelers")
        if request_details.get('budget'):
            text_parts.append(f"Budget: {request_details['budget']}")
    
    # Add message if present
    if request_details.get('message'):
        text_parts.extend([
            "",
            "MESSAGE",
            "-" * 60,
            request_details['message'],
        ])
    
    # Add diver profile if available
    if diver_profile:
        text_parts.extend(["", "DIVER PROFILE (from session)", "-" * 60])
        if diver_profile.get('certification_level'):
            text_parts.append(f"Certification Level: {diver_profile['certification_level']}")
        if diver_profile.get('experience_dives'):
            text_parts.append(f"Experience: {diver_profile['experience_dives']} dives")
        if diver_profile.get('interests'):
            text_parts.append(f"Interests: {', '.join(diver_profile['interests'])}")
        if diver_profile.get('fears'):
            text_parts.append(f"Concerns: {', '.join(diver_profile['fears'])}")
    
    # Add next steps
    text_parts.extend([
        "",
        "NEXT STEPS",
        "-" * 60,
        f"Reply directly to this email to contact {request_details.get('name', 'the inquirer')}",
        f"at {request_details.get('email', 'N/A')}",
        "",
        "=" * 60,
        "This lead was generated by DovvyBuddy, your AI diving assistant",
        f"Lead Reference: {lead.id}",
        "=" * 60,
    ])
    
    return "\n".join(text_parts)
