"""
Form Widget classes specific to the Django admin site.
"""
from __future__ import absolute_import
from itertools import chain
from django import forms
try:
    from django.forms.widgets import ChoiceWidget as RadioChoiceInput
except:
    from django.forms.widgets import RadioChoiceInput
from django.utils.encoding import force_text

from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django.utils.translation import ugettext as _

from .util import vendor, DJANGO_11


class AdminDateWidget(forms.DateInput):

    @property
    def media(self):
        return vendor('datepicker.js', 'datepicker.css', 'xadmin.widget.datetime.js')

    def __init__(self, attrs=None, format=None):
        final_attrs = {'class': 'date-field', 'size': '10'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminDateWidget, self).__init__(attrs=final_attrs, format=format)

    def render(self, name, value, attrs=None):
        input_html = super(AdminDateWidget, self).render(name, value, attrs)
        return mark_safe('<div class="input-group date bootstrap-datepicker"><span class="input-group-addon"><i class="fa fa-calendar"></i></span>%s'
                         '<span class="input-group-btn"><button class="btn btn-default" type="button">%s</button></span></div>' % (input_html, _(u'Today')))


class AdminTimeWidget(forms.TimeInput):

    @property
    def media(self):
        return vendor('datepicker.js', 'clockpicker.js', 'clockpicker.css', 'xadmin.widget.datetime.js')

    def __init__(self, attrs=None, format=None):
        final_attrs = {'class': 'time-field', 'size': '8'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminTimeWidget, self).__init__(attrs=final_attrs, format=format)

    def render(self, name, value, attrs=None):
        input_html = super(AdminTimeWidget, self).render(name, value, attrs)
        return mark_safe('<div class="input-group time bootstrap-clockpicker"><span class="input-group-addon"><i class="fa fa-clock-o">'
                         '</i></span>%s<span class="input-group-btn"><button class="btn btn-default" type="button">%s</button></span></div>' % (input_html, _(u'Now')))


class AdminSelectWidget(forms.Select):

    def render(self, name, value, attrs=None, renderer=None):

        attrs['class'] = attrs.get('class', '') + 'select form-control'

        return super(AdminSelectWidget, self).render(name, value, attrs=attrs, renderer=renderer)

    @property
    def media(self):
        return vendor('select.js', 'select.css', 'xadmin.widget.select.js')


class AdminSplitDateTime(forms.SplitDateTimeWidget):
    """
    A SplitDateTime Widget that has some admin-specific styling.
    """

    def __init__(self, attrs=None):
        widgets = [AdminDateWidget, AdminTimeWidget]
        # Note that we're calling MultiWidget, not SplitDateTimeWidget, because
        # we want to define widgets.
        forms.MultiWidget.__init__(self, widgets, attrs)

    def render(self, name, value, attrs=None):
        if DJANGO_11:
            # insert \n to inputs as separator
            input_html = super(AdminSplitDateTime, self).render(name, value, attrs).replace('/><input', '/>\n<input')

            input_htmls = [ht for ht in input_html.split('\n') if ht != '']
            # return input_html
            return mark_safe('<div class="datetime clearfix"><div class="input-group date bootstrap-datepicker"><span class="input-group-addon"><i class="fa fa-calendar"></i></span>%s'
                             '<span class="input-group-btn"><button class="btn btn-default" type="button">%s</button></span></div>'
                             '<div class="input-group time bootstrap-clockpicker"><span class="input-group-addon"><i class="fa fa-clock-o">'
                             '</i></span>%s<span class="input-group-btn"><button class="btn btn-default" type="button">%s</button></span></div></div>' % (input_htmls[0], _(u'Today'), input_htmls[1], _(u'Now')))
        else:
            return super(AdminSplitDateTime, self).render(name, value, attrs)

    def format_output(self, rendered_widgets):
        return mark_safe(u'<div class="datetime clearfix">%s%s</div>' %
                         (rendered_widgets[0], rendered_widgets[1]))


class AdminRadioInput(forms.CheckboxInput):
    input_type = 'radio'

    def format_value(self, value):
        """Only return the 'value' attribute if value isn't None or boolean."""
        if value is True or value is False or value is None:
            return

        return force_text(value)

    # move to AdminRadioSelect.render to be compatible with django 1.11
#     def render(self, name=None, value=None, attrs=None, choices=()):
#         name = name or self.name
#         value = value or self.value
#         attrs = attrs or self.attrs
#         attrs['class'] = attrs.get('class', '').replace('form-control', '')
#         if 'id' in self.attrs:
#             label_for = ' for="%s_%s"' % (self.attrs['id'], self.index)
#         else:
#             label_for = ''
#         choice_label = conditional_escape(force_text(self.choice_label))
#         if attrs.get('inline', False):
#             return mark_safe(u'<label%s class="radio-inline">%s %s</label>' % (label_for, self.tag(), choice_label))
#         else:
#             return mark_safe(u'<div class="radio"><label%s>%s %s</label></div>' % (label_for, self.tag(), choice_label))


# class AdminRadioFieldRenderer(forms.RadioSelect):
# 
#     def __iter__(self):
#         for i, choice in enumerate(self.choices):
#             yield AdminRadioInput(self.name, self.value, self.attrs.copy(), choice, i)
# 
#     def __getitem__(self, idx):
#         choice = self.choices[idx]  # Let the IndexError propogate
#         return AdminRadioInput(self.name, self.value, self.attrs.copy(), choice, idx)
# 
#     def render(self):
#         return mark_safe(u'\n'.join([force_text(w) for w in self]))


class AdminRadioSelect(RadioChoiceInput):
#     renderer = AdminRadioFieldRenderer
    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            value = []
        elif type(value) not in (list, tuple):
            # convert to list
            value = [value]

        if attrs:
            attrs.update(self.attrs)
        else:
            attrs = self.attrs

        attrs['class'] = attrs.get('class', '').replace('form-control', '')

        if DJANGO_11:
            final_attrs = self.build_attrs(attrs, extra_attrs={'name': name})
        else:
            final_attrs = self.build_attrs(attrs, name=name)
        output = []
        # Normalize to strings
        str_values = set([force_text(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            radio_input = AdminRadioInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_text(option_value)
            rendered_radio_input = radio_input.render(name, option_value)
            option_label = conditional_escape(force_text(option_label))

            if final_attrs.get('inline', False):
                output.append(u'<label class="radio-inline">%s %s</label>' % (rendered_radio_input, option_label))
            else:
                output.append(u'<div class="radio"><label>%s %s</label></div>' % (rendered_radio_input, option_label))

        return mark_safe(u'\n'.join(output))


class AdminCheckboxSelect(RadioChoiceInput):
    allow_multiple_selected = True
    input_type = 'checkbox'

    def __init__(self, attrs=None, can_add_related=True):
        self.can_add_related = can_add_related

        super(AdminCheckboxSelect, self).__init__(attrs=attrs)

    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            value = []

        if attrs:
            attrs.update(self.attrs)
        else:
            attrs = self.attrs

        attrs['class'] = attrs.get('class', '').replace('form-control', '')

        has_id = attrs and 'id' in attrs
        if DJANGO_11:
            final_attrs = self.build_attrs(attrs, extra_attrs={'name': name})
        else:
            final_attrs = self.build_attrs(attrs, name=name)
        output = []
        # Normalize to strings
        str_values = set([force_text(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            cb = forms.CheckboxInput(
                final_attrs, check_test=lambda value: value in str_values)
            option_value = force_text(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_text(option_label))

            if final_attrs.get('inline', False):
                output.append(u'<label%s class="checkbox-inline">%s %s</label>' % (label_for, rendered_cb, option_label))
            else:
                output.append(u'<div class="checkbox"><label%s>%s %s</label></div>' % (label_for, rendered_cb, option_label))
        return mark_safe(u'\n'.join(output))


class AdminSelectMultiple(forms.SelectMultiple):

    def __init__(self, attrs=None):
        final_attrs = {'class': 'select-multi'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminSelectMultiple, self).__init__(attrs=final_attrs)


class AdminFileWidget(forms.ClearableFileInput):
    template_with_initial = (u'<p class="file-upload">%s</p>'
                             % forms.ClearableFileInput.initial_text)
    template_with_clear = (u'<span class="clearable-file-input">%s</span>'
                           % forms.ClearableFileInput.clear_checkbox_label)


class AdminTextareaWidget(forms.Textarea):

    def __init__(self, attrs=None):
        final_attrs = {'class': 'textarea-field'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminTextareaWidget, self).__init__(attrs=final_attrs)


class AdminTextInputWidget(forms.TextInput):
    template_name = 'xadmin/widgets/text.html'

    def __init__(self, attrs=None):
        final_attrs = {'class': 'text-field'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminTextInputWidget, self).__init__(attrs=final_attrs)

    def render(self, name, value, attrs=None):
        if self.attrs.get('readonly') and self.attrs.get('class'):
            # use form-control-static style instead
            self.attrs['class'] = self.attrs['class'].replace('form-control', 'form-control-static')
#             self.attrs['style'] = "padding-top: 0px; border-width: 0px;"
            self.attrs['style'] = "border-width: 0px;"
        return super(AdminTextInputWidget, self).render(name, value, attrs=attrs)


class AdminURLFieldWidget(forms.TextInput):

    def __init__(self, attrs=None):
        final_attrs = {'class': 'url-field'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminURLFieldWidget, self).__init__(attrs=final_attrs)


class AdminIntegerFieldWidget(forms.TextInput):

    def __init__(self, attrs=None):
        final_attrs = {'class': 'int-field'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminIntegerFieldWidget, self).__init__(attrs=final_attrs)


class AdminCommaSeparatedIntegerFieldWidget(forms.TextInput):

    def __init__(self, attrs=None):
        final_attrs = {'class': 'sep-int-field'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminCommaSeparatedIntegerFieldWidget,
              self).__init__(attrs=final_attrs)
