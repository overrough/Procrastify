"""
Register Screen for Procrastify
"""
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder

Builder.load_string('''
<RegisterScreen>:
    name: "register"
    md_bg_color: app.theme_cls.backgroundColor
    
    MDBoxLayout:
        orientation: "vertical"
        padding: "24dp"
        spacing: "16dp"
        
        MDBoxLayout:
            size_hint_y: 0.15
            
        MDLabel:
            text: "Create Account"
            halign: "center"
            font_style: "Display"
            role: "small"
            theme_text_color: "Custom"
            text_color: app.theme_cls.primaryColor
            
        MDLabel:
            text: "Join Procrastify and boost your productivity"
            halign: "center"
            font_style: "Title"
            role: "medium"
            theme_text_color: "Secondary"
            
        MDBoxLayout:
            size_hint_y: 0.05
            
        MDCard:
            orientation: "vertical"
            padding: "24dp"
            spacing: "16dp"
            size_hint_y: None
            height: self.minimum_height
            style: "elevated"
            
            MDTextField:
                id: name_field
                mode: "outlined"
                size_hint_x: 1
                
                MDTextFieldHintText:
                    text: "Full Name"
                    
                MDTextFieldLeadingIcon:
                    icon: "account"
                    
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
                    text: "Password (min 6 characters)"
                    
                MDTextFieldLeadingIcon:
                    icon: "lock"
                    
            MDTextField:
                id: confirm_password_field
                mode: "outlined"
                size_hint_x: 1
                password: True
                
                MDTextFieldHintText:
                    text: "Confirm Password"
                    
                MDTextFieldLeadingIcon:
                    icon: "lock-check"
                    
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
                on_release: root.do_register()
                
                MDButtonText:
                    text: "CREATE ACCOUNT"
                    
            MDButton:
                style: "text"
                size_hint_x: 1
                on_release: root.go_to_login()
                
                MDButtonText:
                    text: "Already have an account? Login"
                    
        MDBoxLayout:
            size_hint_y: 0.2
''')


class RegisterScreen(MDScreen):
    """Registration screen for new users"""
    
    def do_register(self):
        """Attempt to register"""
        name = self.ids.name_field.text.strip()
        email = self.ids.email_field.text.strip()
        password = self.ids.password_field.text
        confirm_password = self.ids.confirm_password_field.text
        
        # Validate inputs
        if not name:
            self.ids.error_label.text = "Please enter your name"
            return
        
        if not email or '@' not in email:
            self.ids.error_label.text = "Please enter a valid email"
            return
        
        if len(password) < 6:
            self.ids.error_label.text = "Password must be at least 6 characters"
            return
        
        if password != confirm_password:
            self.ids.error_label.text = "Passwords do not match"
            return
        
        # Clear error
        self.ids.error_label.text = ""
        
        # Make API call
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        
        result = app.api.register(email, password, name)
        
        if result.get("success"):
            data = result.get("data", {})
            app.login_user(data.get("user"), data.get("token"))
            # Clear fields
            self.ids.name_field.text = ""
            self.ids.email_field.text = ""
            self.ids.password_field.text = ""
            self.ids.confirm_password_field.text = ""
        else:
            error = result.get("data", {}).get("error", result.get("error", "Registration failed"))
            self.ids.error_label.text = error
    
    def go_to_login(self):
        """Navigate to login screen"""
        from kivymd.app import MDApp
        MDApp.get_running_app().go_to_screen('login')
