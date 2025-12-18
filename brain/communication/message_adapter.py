from brain.context.audience_mode import AudienceMode
from brain.communication.tone_profile import ToneProfile
from brain.context.presence_state import PresenceState

class MessageAdapter:
    """
    Adapts message wording based on Audience/Tone.
    Deterministic text transformation (No LLM).
    """
    
    def get_audience(self, presence: PresenceState) -> AudienceMode:
        if presence == PresenceState.ALONE:
            return AudienceMode.PRIVATE
        elif presence == PresenceState.WITH_OTHERS:
            return AudienceMode.PUBLIC
        return AudienceMode.NEUTRAL
        
    def get_tone(self, audience: AudienceMode) -> ToneProfile:
        if audience == AudienceMode.PRIVATE:
            return ToneProfile.PERSONAL
        elif audience == AudienceMode.PUBLIC:
            return ToneProfile.FORMAL
        return ToneProfile.NEUTRAL

    def adapt(self, message: str, tone: ToneProfile) -> str:
        if not message:
            return message
            
        if tone == ToneProfile.FORMAL:
            # Transform "You..." to "System..." or Passive
            if message.lower().startswith("you "):
                return "System Notice: " + message[4:] # "You have..." -> "System Notice: have..." (Naive)
                # Better: "You have a meeting" -> "Meeting scheduled."
                # Hard without NLP. Let's use prefixing for clarity in MVP.
            if "I think" in message:
                return message.replace("I think", "Analysis suggests")
            return f"[System] {message}"
            
        elif tone == ToneProfile.PERSONAL:
            # Ensure warmth
            if not message.lower().startswith("you") and not message.lower().startswith("hey"):
                # Maybe prefix?
                pass
            return message # Default is usually personal
            
        return message
