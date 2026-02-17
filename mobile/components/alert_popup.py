"""
Distraction Alert Popup for Procrastify
Shows when user opens a distracting app during focus session
"""
from kivymd.uix.dialog import MDDialog, MDDialogIcon, MDDialogHeadlineText, MDDialogSupportingText, MDDialogButtonContainer
from kivymd.uix.button import MDButton, MDButtonText


class DistractionAlertPopup:
    """Popup that appears when user is distracted"""
    
    dialog = None
    
    @classmethod
    def show(cls, app_name, time_on_app, current_task=None, on_refocus=None, on_continue=None):
        """
        Show distraction alert popup
        
        Args:
            app_name: Name of the distracting app
            time_on_app: Time spent on app (seconds)
            current_task: Current priority task title
            on_refocus: Callback when user taps Refocus
            on_continue: Callback when user taps Continue
        """
        time_formatted = f"{time_on_app // 60} minutes" if time_on_app >= 60 else f"{time_on_app} seconds"
        
        task_text = f"\n\nYour task: {current_task}" if current_task else ""
        
        message = f"""You've spent {time_formatted} on {app_name}.
        
This is a DISTRACTING app that's taking you away from your goals.{task_text}

Every minute counts. Time to refocus? 🎯"""
        
        def refocus_action(btn):
            cls.dismiss()
            if on_refocus:
                on_refocus()
        
        def continue_action(btn):
            cls.dismiss()
            if on_continue:
                on_continue()
        
        cls.dialog = MDDialog(
            MDDialogIcon(icon="alert"),
            MDDialogHeadlineText(text="⚠️ Distraction Detected!"),
            MDDialogSupportingText(text=message),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Continue Anyway"),
                    style="text",
                    on_release=continue_action
                ),
                MDButton(
                    MDButtonText(text="🎯 REFOCUS NOW"),
                    style="filled",
                    on_release=refocus_action
                ),
            )
        )
        cls.dialog.open()
    
    @classmethod
    def dismiss(cls):
        """Dismiss the dialog"""
        if cls.dialog:
            cls.dialog.dismiss()
            cls.dialog = None
