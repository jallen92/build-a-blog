#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import os
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape= True)

class Posts(db.Model):
    title = db.StringProperty(required=True)
    body = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add= True)


class MainHandler(webapp2.RequestHandler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM Posts ORDER BY created DESC LIMIT 5")
        t = jinja_env.get_template("frontpage.html")
        content = t.render(posts = posts)
        self.response.write(content)



class NewPostHandler(webapp2.RequestHandler):
    def get(self):
        t = jinja_env.get_template("new-post.html")
        content = t.render(
            title = self.request.get("title"),
            body = self.request.get("body"),
            error = "")
        self.response.write(content)

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            post = Posts(title=title, body=body)
            post.put()
            self.redirect("/blog/{}".format(post.key().id()))
        else:
            error = "Please insert both a title and body for your blog post."
            t = jinja_env.get_template("new-post.html")
            content = t.render(
                title = self.request.get("title"),
                body = self.request.get("body"),
                error = error)
            self.response.write(content)

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        post = Posts.get_by_id(int(id))
        t = jinja_env.get_template("post.html")
        content = t.render(post = post)
        self.response.write(content)





app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/blog', MainHandler),
    ('/new-post', NewPostHandler),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
