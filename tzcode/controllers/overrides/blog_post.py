from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.website.doctype.blog_post.blog_post import BlogPost as ERPNextBlogPost


class BlogPost(ERPNextBlogPost):
    def validate(self):
        pass


