"""
Login Screen for Procrastify
"""
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel
from kivy.properties import ObjectProperty
from kivy.lang import Builder

Builder.load_string('''
<LoginScreen>:
    name: "login"
    md_bg_color: app.theme_cls.backgroundColor
    
    MDBoxLayout:
        orientation: "vertical"
        padding: "24dp"
        spacing: "16dp"
        
        MDBoxLayout:
            size_hint_y: 0.3
            
        MDLabel:
            text: "🎯 Procrastify"
            halign: "center"
            font_style: "Display"
            role: "small"
            theme_text_color: "Custom"
            text_color: app.theme_cls.primaryColor
            
        MDLabel:
            text: "Beat Procrastination. Stay Focused."
            halign: "center"
            font_style: "Title"
            role: "medium"
            theme_text_color: "Secondary"
            
        MDBoxLayout:
            size_hint_y: 0.1
            
        MDCard:
            orientation: "vertical"
            padding: "24dp"
            spacing: "16dp"
            size_hint_y: None
            height: self.minimum_height
            style: "elevated"
            
            MDTextField:
                id: email_field
                mode: "outlined"
                size_hint_x: 1
                
                MDTextFieldHintText:
                    text: "Email"
                    
                MDTextFieldLeadingIcon:
                    icon: "email"
                    
            MDTextField:
                id: password_field
                mode: "outlined"
                size_hint_x: 1
                password: True
                
                MDTextFieldHintText:
                    text: "Password"
                    
                MDTextFieldLeadingIcon:
                    icon: "lock"
                    
            MDLabel:
                id: error_label
                text: ""
                halign: "center"
                theme_text_color: "Error"
                size_hint_y: None
                height: "24dp"
                    
            MDButton:
                style: "filled"
                size_hint_x: 1
                on_release: root.do_login()
                
                MDButtonText:
                    text: "LOGIN"
                    
            MDButton:
                style: "text"
                size_hint_x: 1
                on_release: root.go_to_register()
                
                MDButtonText:
                    text: "Don't have an account? Register"
                    
        MDBoxLayout:
            size_hint_y: 0.3
''')


class LoginScreen(MDScreen):
    """Login screen with email and password fields"""
    
    def do_login(self):
        """Attempt to login"""
        email = self.ids.email_field.text.strip()
        password = self.ids.password_field.text
        
        # Validate inputs
        if not email:
            self.ids.error_label.text = "Please enter your email"
            return
        
        if not password:
            self.ids.error_label.text = "Please enter your password"
            return
        
        # Clear error
        self.ids.error_label.text = ""
        
        # Make API call
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        
        result = app.api.login(email, password)
        
        if result.get("success"):
            data = result.get("data", {})
            app.login_user(data.get("user"), data.get("token"))
            # Clear fields
            self.ids.email_field.text = ""
            self.ids.password_field.text = ""
        else:
            error = result.get("data", {}).get("error", result.get("error", "Login failed"))
            self.ids.error_label.text = error
    
    def go_to_register(self):
        """Navigate to register screen"""
        from kivymd.app import MDApp
        MDApp.get_running_app().go_to_screen('register')
