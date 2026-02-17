"""
Tasks Screen for Procrastify
Task list with add/edit/complete/delete functionality
"""
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog, MDDialogIcon, MDDialogHeadlineText, MDDialogSupportingText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText, MDListItemSupportingText, MDListItemLeadingIcon, MDListItemTrailingCheckbox
from kivymd.uix.menu import MDDropdownMenu
from kivy.lang import Builder
from kivy.metrics import dp
from datetime import datetime, timedelta

Builder.load_string('''
<TasksScreen>:
    name: "tasks"
    md_bg_color: app.theme_cls.backgroundColor
    
    MDBoxLayout:
        orientation: "vertical"
        
        MDTopAppBar:
            title: "My Tasks"
            type: "small"
            
            MDTopAppBarLeadingButtonContainer:
                MDActionTopAppBarButton:
                    icon: "arrow-left"
                    on_release: app.go_to_screen('home')
                    
            MDTopAppBarTrailingButtonContainer:
                MDActionTopAppBarButton:
                    icon: "filter"
                    on_release: root.show_filter_menu()
                    
                MDActionTopAppBarButton:
                    icon: "refresh"
                    on_release: root.load_tasks()
                    
        # Task Stats
        MDCard:
            orientation: "horizontal"
            padding: "16dp"
            size_hint_y: None
            height: "80dp"
            style: "elevated"
            md_bg_color: app.theme_cls.primaryContainerColor
            
            MDBoxLayout:
                orientation: "vertical"
                
                MDLabel:
                    id: overdue_label
                    text: "0 Overdue"
                    font_style: "Body"
                    role: "large"
                    theme_text_color: "Error"
                    
                MDLabel:
                    id: high_priority_label
                    text: "0 High Priority"
                    font_style: "Body"
                    role: "medium"
                    theme_text_color: "Secondary"
                    
            MDBoxLayout:
                orientation: "vertical"
                
                MDLabel:
                    id: total_label
                    text: "0 Total"
                    font_style: "Body"
                    role: "large"
                    
                MDLabel:
                    id: completed_label
                    text: "0 Completed"
                    font_style: "Body"
                    role: "medium"
                    theme_text_color: "Secondary"
                    
        # Category Tabs
        MDBoxLayout:
            size_hint_y: None
            height: "48dp"
            padding: "8dp", 0
            spacing: "8dp"
            
            MDButton:
                id: all_btn
                style: "filled"
                on_release: root.filter_category('all')
                
                MDButtonText:
                    text: "All"
                    
            MDButton:
                id: study_btn
                style: "outlined"
                on_release: root.filter_category('Study')
                
                MDButtonText:
                    text: "Study"
                    
            MDButton:
                id: work_btn
                style: "outlined"
                on_release: root.filter_category('Work')
                
                MDButtonText:
                    text: "Work"
                    
            MDButton:
                id: personal_btn
                style: "outlined"
                on_release: root.filter_category('Personal')
                
                MDButtonText:
                    text: "Personal"
                    
        # Task List
        ScrollView:
            MDList:
                id: tasks_list
                
        # Add Task FAB
        MDButton:
            style: "filled"
            pos_hint: {"center_x": 0.5}
            on_release: root.show_add_task_dialog()
            
            MDButtonIcon:
                icon: "plus"
                
            MDButtonText:
                text: "Add Task"
''')


class TasksScreen(MDScreen):
    """Task management screen with CRUD operations"""
    
    dialog = None
    current_filter = "all"
    tasks_data = []
    
    def on_enter(self):
        """Called when screen is displayed"""
        self.load_tasks()
    
    def load_tasks(self, status="pending"):
        """Load tasks from API"""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        
        result = app.api.get_tasks(status)
        
        # Clear existing
        self.ids.tasks_list.clear_widgets()
        
        if result.get("success"):
            data = result.get("data", {})
            self.tasks_data = data.get("tasks", [])
            summary = data.get("summary", {})
            
            # Update stats
            self.ids.overdue_label.text = f"{summary.get('overdue', 0)} Overdue"
            self.ids.high_priority_label.text = f"{summary.get('high', 0)} High Priority"
            self.ids.total_label.text = f"{summary.get('total', 0)} Total"
            
            # Filter tasks
            filtered = self.tasks_data
            if self.current_filter != "all":
                filtered = [t for t in self.tasks_data if t.get("category") == self.current_filter]
            
            # Display tasks
            for task in filtered:
                self.add_task_to_list(task)
            
            if not filtered:
                item = MDListItem(
                    MDListItemLeadingIcon(icon="check-all"),
                    MDListItemHeadlineText(text="No tasks found"),
                    MDListItemSupportingText(text="Tap 'Add Task' to create one!")
                )
                self.ids.tasks_list.add_widget(item)
    
    def add_task_to_list(self, task):
        """Add a task item to the list"""
        urgency = task.get("urgency_level", "MEDIUM")
        color = task.get("urgency_color", "#FFFFFF")
        days = task.get("days_remaining", 0)
        
        if urgency == "OVERDUE":
            icon = "alert-circle"
            days_text = "OVERDUE"
        elif urgency == "HIGH":
            icon = "alert"
            days_text = f"{days} day{'s' if days != 1 else ''} left"
        else:
            icon = "checkbox-blank-circle-outline"
            days_text = f"{days} day{'s' if days != 1 else ''} left"
        
        task_id = task.get("task_id")
        
        item = MDListItem(
            MDListItemLeadingIcon(
                icon=icon,
                theme_icon_color="Custom",
                icon_color=color
            ),
            MDListItemHeadlineText(text=task.get("title", "Task")),
            MDListItemSupportingText(text=f"{task.get('category', 'Study')} • {days_text} • Complexity: {task.get('complexity', 1)}/5"),
            MDListItemTrailingCheckbox(
                on_active=lambda cb, active, tid=task_id: self.on_task_checked(tid, active)
            )
        )
        item.task_id = task_id
        
        self.ids.tasks_list.add_widget(item)
    
    def on_task_checked(self, task_id, active):
        """Handle task completion"""
        if active:
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            
            result = app.api.complete_task(task_id)
            if result.get("success"):
                app.show_snackbar("Task completed! 🎉")
                self.load_tasks()
    
    def filter_category(self, category):
        """Filter tasks by category"""
        self.current_filter = category
        
        # Update button styles
        buttons = ['all_btn', 'study_btn', 'work_btn', 'personal_btn']
        categories = ['all', 'Study', 'Work', 'Personal']
        
        for btn, cat in zip(buttons, categories):
            if cat == category:
                self.ids[btn].style = "filled"
            else:
                self.ids[btn].style = "outlined"
        
        self.load_tasks()
    
    def show_filter_menu(self):
        """Show status filter menu"""
        from kivymd.app import MDApp
        
        menu_items = [
            {"text": "Pending Tasks", "on_release": lambda: self.menu_callback("pending")},
            {"text": "Completed Tasks", "on_release": lambda: self.menu_callback("completed")},
            {"text": "All Tasks", "on_release": lambda: self.menu_callback("all")},
        ]
        
        self.menu = MDDropdownMenu(
            items=menu_items,
            width_mult=3,
        )
        self.menu.open()
    
    def menu_callback(self, status):
        """Handle menu selection"""
        self.menu.dismiss()
        self.load_tasks(status)
    
    def show_add_task_dialog(self):
        """Show dialog to add new task"""
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
        from kivymd.uix.segmentedbutton import MDSegmentedButton, MDSegmentedButtonItem, MDSegmentButtonLabel
        
        content = MDBoxLayout(
            orientation="vertical",
            spacing="16dp",
            padding="16dp",
            size_hint_y=None,
        )
        content.height = dp(280)
        
        # Title field
        title_field = MDTextField(mode="outlined", size_hint_x=1)
        title_field.add_widget(MDTextFieldHintText(text="Task Title"))
        content.add_widget(title_field)
        
        # Deadline (days from now)
        deadline_field = MDTextField(mode="outlined", size_hint_x=1)
        deadline_field.add_widget(MDTextFieldHintText(text="Days until deadline (e.g., 3)"))
        content.add_widget(deadline_field)
        
        # Complexity
        complexity_field = MDTextField(mode="outlined", size_hint_x=1)
        complexity_field.add_widget(MDTextFieldHintText(text="Complexity (1-5)"))
        content.add_widget(complexity_field)
        
        # Store references
        self.add_title_field = title_field
        self.add_deadline_field = deadline_field
        self.add_complexity_field = complexity_field
        
        self.dialog = MDDialog(
            MDDialogIcon(icon="checkbox-marked-outline"),
            MDDialogHeadlineText(text="Add New Task"),
            MDDialogContentContainer(content),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Cancel"),
                    style="text",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDButton(
                    MDButtonText(text="Add"),
                    style="filled",
                    on_release=lambda x: self.add_task()
                ),
            )
        )
        self.dialog.open()
    
    def add_task(self):
        """Add task from dialog"""
        title = self.add_title_field.text.strip()
        days_str = self.add_deadline_field.text.strip()
        complexity_str = self.add_complexity_field.text.strip()
        
        # Validate
        if not title:
            return
        
        try:
            days = int(days_str)
            complexity = int(complexity_str)
            if complexity < 1 or complexity > 5:
                complexity = 3
        except:
            days = 7
            complexity = 3
        
        # Calculate deadline
        deadline = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        
        # Make API call
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        
        result = app.api.create_task(title, deadline, complexity)
        
        if result.get("success"):
            self.dialog.dismiss()
            app.show_snackbar(f"Task '{title}' added!")
            self.load_tasks()
        else:
            app.show_snackbar("Failed to add task")
