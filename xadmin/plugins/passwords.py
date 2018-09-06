# coding=utf-8
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import password_reset_confirm
# from django.contrib.auth.models import User
from django.db.models import Q
from django.template.response import TemplateResponse
from django.utils.translation import ugettext as _

from xadmin.sites import site
from xadmin.views.base import BaseAdminPlugin, BaseAdminView, csrf_protect_m
from xadmin.views.website import LoginView


class MyPasswordResetForm(PasswordResetForm):
    def clean(self):
        email = self.cleaned_data.get('email')
        
        if email:
            matching_users = get_user_model()._default_manager.filter(Q(username__iexact=email)|Q(email__iexact=email))
            if not matching_users.exists():
                # check if this email is registered?
                self.errors["email"] = self.error_class([_('this email is not registered!')])
            
            elif not matching_users.filter(is_active=True).exists():
                # check if this user is active?
                self.errors["email"] = self.error_class([_('this account has been revoked!')])                

        return self.cleaned_data

    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.

        """
        active_users = get_user_model()._default_manager.filter(
            Q(username__iexact=email)|Q(email__iexact=email), is_active=True)
        return (u for u in active_users if u.has_usable_password())


class ResetPasswordSendView(BaseAdminView):

    need_site_permission = False

    password_reset_form = MyPasswordResetForm
    password_reset_template = 'xadmin/auth/password_reset/form.html'
    password_reset_done_template = 'xadmin/auth/password_reset/done.html'
    password_reset_token_generator = default_token_generator

    password_reset_from_email = None
    password_reset_email_template = 'xadmin/auth/password_reset/email.html'
    password_reset_subject_template = None

    def get(self, request, *args, **kwargs):
        context = super(ResetPasswordSendView, self).get_context()
        context['form'] = kwargs.get('form', self.password_reset_form())

        return TemplateResponse(request, self.password_reset_template, context)

    @csrf_protect_m
    def post(self, request, *args, **kwargs):
        form = self.password_reset_form(request.POST)

        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': self.password_reset_token_generator,
                'email_template_name': self.password_reset_email_template,
                'request': request,
                'domain_override': request.get_host(),
                # 強制修改site_name
                'extra_email_context': {'site_name': self.site_title}
            }

            if self.password_reset_from_email:
                opts['from_email'] = self.password_reset_from_email
            if self.password_reset_subject_template:
                opts['subject_template_name'] = self.password_reset_subject_template

            form.save(**opts)
            context = super(ResetPasswordSendView, self).get_context()
            return TemplateResponse(request, self.password_reset_done_template, context)
        else:
            return self.get(request, form=form)

site.register_view(r'^password_reset/$', ResetPasswordSendView, name='xadmin_password_reset')

class ResetLinkPlugin(BaseAdminPlugin):

    def block_form_bottom(self, context, nodes):
        reset_link = self.get_admin_url('xadmin_password_reset')
        return '<div class="text-right" style="margin-top:15px;"><a href="%s" class="text-muted"><i class="fa fa-question-circle"></i> %s</a></div>' % (reset_link, _('Forgotten your password or username?'))

site.register_plugin(ResetLinkPlugin, LoginView)


class ResetPasswordComfirmView(BaseAdminView):

    need_site_permission = False

    password_reset_set_form = SetPasswordForm
    password_reset_confirm_template = 'xadmin/auth/password_reset/confirm.html'
    password_reset_token_generator = default_token_generator

    def do_view(self, request, uidb36, token, *args, **kwargs):
        context = super(ResetPasswordComfirmView, self).get_context()
        return password_reset_confirm(request, uidb36, token,
                   template_name=self.password_reset_confirm_template,
                   token_generator=self.password_reset_token_generator,
                   set_password_form=self.password_reset_set_form,
                   post_reset_redirect=self.get_admin_url('xadmin_password_reset_complete'),
                   current_app=self.admin_site.name, extra_context=context)

    def get(self, request, uidb36, token, *args, **kwargs):
        return self.do_view(request, uidb36, token)

    def post(self, request, uidb36, token, *args, **kwargs):
        return self.do_view(request, uidb36, token)

    def get_media(self):
        return super(ResetPasswordComfirmView, self).get_media() + \
            self.vendor('xadmin.page.form.js', 'xadmin.form.css')

site.register_view(r'^password_reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    ResetPasswordComfirmView, name='xadmin_password_reset_confirm')


class ResetPasswordCompleteView(BaseAdminView):

    need_site_permission = False

    password_reset_complete_template = 'xadmin/auth/password_reset/complete.html'

    def get(self, request, *args, **kwargs):
        context = super(ResetPasswordCompleteView, self).get_context()
        context['login_url'] = self.get_admin_url('index')

        return TemplateResponse(request, self.password_reset_complete_template, context)

site.register_view(r'^password_reset/complete/$', ResetPasswordCompleteView, name='xadmin_password_reset_complete')

