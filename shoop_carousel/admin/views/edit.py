# -*- coding: utf-8 -*-
# This file is part of Shoop Carousel.
#
# Copyright (c) 2012-2015, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals

from django.conf import settings
from django.db.transaction import atomic
from shoop.admin.form_part import FormPart, FormPartsViewMixin, SaveFormPartsMixin, TemplatedFormDef
from shoop.admin.utils.views import CreateOrUpdateView
from shoop.admin.toolbar import get_default_edit_toolbar

from shoop_carousel.admin.forms import CarouselForm, SlideFormSet
from shoop_carousel.models import Carousel


class CarouselFormPart(FormPart):
    priority = 1
    name = "base"
    form = CarouselForm

    def get_form_defs(self):
        yield TemplatedFormDef(
            self.name,
            self.form,
            template_name="shoop_carousel/admin/_edit_base_form.jinja",
            required=True,
            kwargs={
                "instance": self.object,
            }
        )

    def form_valid(self, form):
        self.object = form[self.name].save()
        return self.object


class SlideFormPart(FormPart):
    priority = 2
    name = "slides"
    formset = SlideFormSet

    def get_form_defs(self):
        yield TemplatedFormDef(
            self.name,
            self.formset,
            template_name="shoop_carousel/admin/_edit_slide_form.jinja",
            required=False,
            kwargs={"carousel": self.object, "languages": settings.LANGUAGES}
        )

    def form_valid(self, form):
        if self.name in form.forms:
            form.forms[self.name].save()


class CarouselEditView(FormPartsViewMixin, SaveFormPartsMixin, CreateOrUpdateView):
    model = Carousel
    template_name = "shoop_carousel/admin/edit.jinja"
    base_form_part_classes = [
        CarouselFormPart,
        SlideFormPart,
    ]
    context_object_name = "carousel"
    form_part_class_provide_key = "admin_carousel_form_part"

    def get_toolbar(self):
        save_form_id = self.get_save_form_id()
        if save_form_id:
            return get_default_edit_toolbar(self, save_form_id, delete_url="shoop_admin:carousel.delete")

    @atomic
    def form_valid(self, form):
        return self.save_form_parts(form)