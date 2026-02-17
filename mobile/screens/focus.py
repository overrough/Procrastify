"""
Focus Session Screen for Procrastify
Pomodoro timer with task linking
"""
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import NumericProperty, BooleanProperty, StringProperty

Builder.load_string('''
<FocusScreen>:
    name: "focus"
    md_bg_color: app.theme_cls.backgroundColor
    
    MDBoxLayout:
        orientation: "vertical"
        
        MDTopAppBar:
            title: "Focus Timer"
            type: "small"
            
            MDTopAppBarLeadingButtonContainer:
                MDActionTopAppBarButton:
                    icon: "arrow-left"
                    on_release: root.confirm_exit()
                    
        MDBoxLayout:
            orientation: "vertical"
            padding: "24dp"
            spacing: "24dp"
            
            # Timer Display
            MDCard:
                orientation: "vertical"
                padding: "32dp"
                size_hint_y: None
                height: "320dp"
                style: "elevated"
                md_bg_color: app.theme_cls.primaryContainerColor
                
                MDLabel:
                    id: status_label
                    text: "Ready to Focus?"
                    font_style: "Title"
                    role: "large"
                    halign: "center"
                    
                MDLabel:
                    id: timer_label
                    text: "25:00"
                    font_style: "Display"
                    role: "large"
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: app.theme_cls.primaryColor
                    
                MDLabel:
                    id: task_label
                    text: "No task selected"
                    font_style: "Body"
                    role: "large"
                    halign: "center"
                    theme_text_color: "Secondary"
                    
                MDBoxLayout:
                    size_hint_y: None
                    height: "60dp"
                    spacing: "16dp"
                    padding: "24dp", "16dp"
                    
                    MDButton:
                        id: start_btn
                        style: "filled"
                        on_release: root.toggle_timer()
                        size_hint_x: 1
                        
                        MDButtonIcon:
                            id: start_icon
                            icon: "play"
                            
                        MDButtonText:
                            id: start_text
                            text: "START"
                            
                    MDButton:
                        id: reset_btn
                        style: "outlined"
                        on_release: root.reset_timer()
                        
                        MDButtonIcon:
                            icon: "refresh"
                            
            # Session Info
            MDCard:
                orientation: "vertical"
                padding: "20dp"
                size_hint_y: None
                height: "140dp"
                style: "elevated"
                
                MDLabel:
                    text: "Session Stats"
                    font_style: "Title"
                    role: "medium"
                    
                MDBoxLayout:
                    spacing: "16dp"
                    padding: 0, "12dp", 0, 0
                    
                    MDBoxLayout:
                        orientation: "vertical"
                        
                        MDLabel:
                            id: sessions_today_label
                            text: "0"
                            font_style: "Headline"
                            role: "medium"
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: app.theme_cls.primaryColor
                            
                        MDLabel:
                            text: "Today"
                            font_style: "Body"
                            role: "small"
                            halign: "center"
                            theme_text_color: "Secondary"
                            
                    MDBoxLayout:
                        orientation: "vertical"
                        
                        MDLabel:
                            id: streak_label
                            text: "0"
                            font_style: "Headline"
                            role: "medium"
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: app.theme_cls.primaryColor
                            
                        MDLabel:
                            text: "Streak"
                            font_style: "Body"
                            role: "small"
                            halign: "center"
                            theme_text_color: "Secondary"
                            
                    MDBoxLayout:
                        orientation: "vertical"
                        
                        MDLabel:
                            id: total_time_label
                            text: "0m"
                            font_style: "Headline"
                            role: "medium"
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: app.theme_cls.primaryColor
                            
                        MDLabel:
                            text: "Total"
                            font_style: "Body"
                            role: "small"
                            halign: "center"
                            theme_text_color: "Secondary"
                            
            # Quick Tips
            MDCard:
                orientation: "vertical"
                padding: "16dp"
                size_hint_y: None
                height: "100dp"
                style: "outlined"
                
                MDLabel:
                    id: tip_label
                    text: "💡 Tip: Put your phone face down during focus sessions"
                    font_style: "Body"
                    role: "medium"
                    halign: "center"
                    theme_text_color: "Secondary"
''')


class FocusScreen(MDScreen):
    """Pomodoro focus timer screen"""
    
    # Timer properties
    time_remaining = NumericProperty(25 * 60)  # 25 minutes in seconds
    is_running = BooleanProperty(False)
    is_break = BooleanProperty(False)
    
    # Session data
    session_id = None
    current_task_id = None
    interruptions = 0
    
    # Clock event
    timer_event = None
    
    FOCUS_DURATION = 25 * 60  # 25 minutes
    BREAK_DURATION = 5 * 60   # 5 minutes
    
    tips = [
        "💡 Put your phone face down during focus",
        "💡 Close unnecessary tabs before starting",
        "💡 Take a short walk during breaks",
        "💡 Stay hydrated - keep water nearby",
        "💡 One task at a time = better focus",
        "💡 Small progress is still progress!",
    ]
    tip_index = 0
    
    def on_enter(self):
        """Called when screen is displayed"""
        self.load_stats()
        self.update_tip()
    
    def on_leave(self):
        """Called when leaving screen"""
        pass  # Don't stop timer when leaving
    
    def load_stats(self):
        """Load session statistics"""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        
        # Get daily analytics
        result = app.api.get_daily_analytics()
        if result.get("success"):
            data = result.get("data", {})
            self.ids.sessions_today_label.text = str(data.get("focus_sessions", 0))
        
        # Get streak
        result = app.api.get_streak()
        if result.get("success"):
            data = result.get("data", {})
            self.ids.streak_label.text = str(data.get("streak", 0))
        
        # Get session stats
        result = app.api.get_session_stats()
        if result.get("success"):
            data = result.get("data", {})
            total_time = data.get("total_focus_time", 0)
            if total_time < 60:
                self.ids.total_time_label.text = f"{total_time}m"
            else:
                self.ids.total_time_label.text = f"{total_time // 60}h"
    
    def toggle_timer(self):
        """Start or pause the timer"""
        if self.is_running:
            self.pause_timer()
        else:
            self.start_timer()
    
    def start_timer(self):
        """Start the timer"""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        
        # Start session if not already started
        if not self.session_id and not self.is_break:
            result = app.api.start_session(self.current_task_id)
            if result.get("success"):
                data = result.get("data", {})
                self.session_id = data.get("session_id")
        
        self.is_running = True
        self.ids.start_icon.icon = "pause"
        self.ids.start_text.text = "PAUSE"
        self.ids.status_label.text = "Break Time! 🧘" if self.is_break else "Stay Focused! 🎯"
        
        # Start clock
        self.timer_event = Clock.schedule_interval(self.update_timer, 1)
    
    def pause_timer(self):
        """Pause the timer"""
        self.is_running = False
        self.ids.start_icon.icon = "play"
        self.ids.start_text.text = "RESUME"
        self.ids.status_label.text = "Paused"
        self.interruptions += 1
        
        if self.timer_event:
            self.timer_event.cancel()
    
    def reset_timer(self):
        """Reset the timer"""
        if self.timer_event:
            self.timer_event.cancel()
        
        self.is_running = False
        self.is_break = False
        self.time_remaining = self.FOCUS_DURATION
        self.session_id = None
        self.interruptions = 0
        
        self.ids.start_icon.icon = "play"
        self.ids.start_text.text = "START"
        self.ids.status_label.text = "Ready to Focus?"
        self.update_timer_display()
    
    def update_timer(self, dt):
        """Update timer every second"""
        if self.time_remaining > 0:
            self.time_remaining -= 1
            self.update_timer_display()
        else:
            self.timer_complete()
    
    def update_timer_display(self):
        """Update the timer label"""
        minutes = int(self.time_remaining // 60)
        seconds = int(self.time_remaining % 60)
        self.ids.timer_label.text = f"{minutes:02d}:{seconds:02d}"
    
    def timer_complete(self):
        """Handle timer completion"""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        
        if self.timer_event:
            self.timer_event.cancel()
        
        self.is_running = False
        
        if self.is_break:
            # Break complete, ready for next focus
            self.is_break = False
            self.time_remaining = self.FOCUS_DURATION
            self.ids.status_label.text = "Break Over! Ready for more? 💪"
            self.ids.start_icon.icon = "play"
            self.ids.start_text.text = "START"
            app.show_snackbar("Break complete! Ready for another session?")
        else:
            # Focus session complete
            if self.session_id:
                # Calculate focus score (simplified)
                focus_score = max(0, 100 - (self.interruptions * 10))
                
                app.api.end_session(
                    self.session_id,
                    completed=True,
                    interruptions=self.interruptions,
                    focus_score=focus_score
                )
                self.session_id = None
            
            # Switch to break
            self.is_break = True
            self.time_remaining = self.BREAK_DURATION
            self.interruptions = 0
            self.ids.status_label.text = "Great work! Take a break! 🎉"
            self.ids.start_icon.icon = "play"
            self.ids.start_text.text = "START BREAK"
            
            app.show_snackbar("Focus session complete! 🎉 Take a break!")
            self.load_stats()
        
        self.update_timer_display()
        self.update_tip()
    
    def update_tip(self):
        """Rotate tips"""
        self.ids.tip_label.text = self.tips[self.tip_index % len(self.tips)]
        self.tip_index += 1
    
    def confirm_exit(self):
        """Confirm before exiting during active session"""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        
        if self.is_running:
            # Show warning
            app.show_snackbar("Paused. Press back again to exit.")
            self.pause_timer()
        else:
            app.go_to_screen('home')
