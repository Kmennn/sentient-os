
import sys
import os
import time
import json
import logging

# Setup path
sys.path.append(os.getcwd())

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VERIFY")

def test_app_context():
    logger.info("--- TEST 1: REAL APP CONTEXT (Window Title) ---")
    try:
        from brain.context.signals.app_context_provider import AppContextProvider
        provider = AppContextProvider()
        ctx = provider.get_context()
        if ctx:
            logger.info(f"✅ REAL CONTEXT DETECTED: {ctx.data}")
        else:
            logger.warning("⚠️ No context detected (OS might be locked/idle or non-Windows)")
    except Exception as e:
        logger.error(f"❌ AppContext Failed: {e}")

def test_voice():
    logger.info("--- TEST 2: REAL VOICE OUTPUT (pyttsx3) ---")
    try:
        from brain.output.voice_output_manager import VoiceOutputManager
        vm = VoiceOutputManager()
        vm.speak("System verification complete. Real voice engine active.", force=True)
        logger.info("✅ Voice signal sent to engine (Listen for audio)")
    except Exception as e:
        logger.error(f"❌ Voice Failed: {e}")

def test_action_exec():
    logger.info("--- TEST 3: REAL NATIVE EXECUTION (Subprocess) ---")
    try:
        from brain.actions.action_executor import ActionSandbox, ActionCapability, ActionRisk
        # Mock dependencies
        class MockLedger: 
            def append(self, x): pass
        class MockScheduler:
            def is_safe_to_execute(self, x): return True
            def record_action_outcome(self, x, y): pass
            execution_store = None
            device_trust_score = 100
            active_device_id = "test_dev"
            
        sandbox = ActionSandbox(MockLedger(), MockScheduler())
        
        # Manually register since we are checking the new capability
        # (It should be auto-registered in __init__ but let's be sure)
        if "native_exec" not in sandbox._capabilities:
            logger.error("❌ 'native_exec' capability NOT found!")
            return

        # Params
        sandbox._capabilities["native_exec"].params = {"command": "echo REAL_EXEC_SUCCESS"}
        
        res = sandbox.execute_action("native_exec")
        if res.status.value == "success":
            logger.info("✅ Native Action Executed Successfully (Check console for 'REAL_EXEC_SUCCESS')")
        else:
            logger.error(f"❌ Native Action Failed: {res.error_reason}")
            
    except Exception as e:
        logger.error(f"❌ Action Exec Failed: {e}")

def test_vision_lib():
    logger.info("--- TEST 4: REAL VISION CAPTURE (PyAutoGUI) ---")
    try:
        import pyautogui
        try:
            # Taking screenshot
            sc = pyautogui.screenshot()
            logger.info(f"✅ Screenshot Captured: {sc.size} pixels")
        except OSError:
             # Headless environments (CI) fail here, but user is on Windows Desktop
             logger.warning("⚠️ Screenshot failed (No Display?)")
    except ImportError:
        logger.error("❌ PyAutoGUI not installed.")
    except Exception as e:
        logger.error(f"❌ Vision Failed: {e}")

if __name__ == "__main__":
    logger.info("Starting Verification of REAL Capabilities...")
    test_app_context()
    time.sleep(1)
    test_action_exec()
    time.sleep(1)
    test_vision_lib()
    time.sleep(1)
    test_voice()
    logger.info("Verification Complete.")
