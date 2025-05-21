# dashboard/views/dashboards.py
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect

class RoleAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    role_required = None
    
    def test_func(self):
        return self.request.user.role == self.role_required
    
    def handle_no_permission(self):
        return redirect('login')

class StudentDashboard(RoleAccessMixin, TemplateView):
    template_name = 'dashboards/student.html'
    role_required = 'student'

class TeacherDashboard(RoleAccessMixin, TemplateView):
    template_name = 'dashboards/teacher.html' 
    role_required = 'teacher'

class AdminDashboard(RoleAccessMixin, TemplateView):
    template_name = 'dashboards/admin.html'
    role_required = 'admin'