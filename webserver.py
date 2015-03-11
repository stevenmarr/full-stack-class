from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
import cgi
import urllib2

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)


class webServerHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			if self.path.endswith("/hello"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				message = ""
				message += "<html><body>"
				message += "<h1>Hello</h1>"
				message += '''<form method='POST' action='/hello'  enctype='multipart/form-data'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
				message += "</body></html>"
				self.wfile.write(message)
				print message
				return
			if self.path.endswith("/hola"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				message = ""
				message += "<html><body>"
				message += "<h1>&#161 Hola !</h1>"
				message += '''<form method='POST' action='/hello' enctype='multipart/form-data'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
				message += "</body></html>"
				self.wfile.write(message)
				print message
				return
			if self.path.endswith("/restaurant/new"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				message = ""
				message += "<html><body>"
				message += "<h1>Create a new resturant</h1>"
				message += '''<form method='POST' action='/restaurant/new' enctype='multipart/form-data'><h2>New restaurant name</h2><input name="restaurant_name" type="text" ><input type="submit" value="Submit"> </form>'''
				message += "</body></html>"
				self.wfile.write(message)
				print message
				return		
			if self.path.endswith("/restaurant"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				session = DBSession()
				restaurants = session.query(Restaurant).all()
				message = ""
				message += "<html><body>"
				message += "<h1>Restaurants</h1>"
				message += "<a href=/restaurant/new>Add Restaurant</a>"
				for restaurant in restaurants:
					edit_url = "/restaurant/%s/edit"% restaurant.id
					delete_url = "/restaurant/%s/delete"% restaurant.id
					message += "<div><h2>%s</h2><a href=\"%s\">Edit</a></br><a href=\"%s\">Delete</a></div>"\
								% (restaurant.name,edit_url,delete_url)
				message += "</body></html>"
				self.wfile.write(message)
				
				print message
				return
			if self.path.endswith("/edit"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				id = self.path.split('/')[2]
				session = DBSession()
				restaurant = session.query(Restaurant).filter_by(id = id).one()
				message = ""
				message += "<html><body>"
				message += "<h1>Create a new resturant</h1>"
				message += "<form method='POST' action='/restaurant/%s/edit' enctype='multipart/form-data'>"% (id)
				message += "<h2>Edit restaurant name</h2><input name=\"restaurant_name\" type=\"text\" value=\"%s\">"% restaurant.name
				message += "<input type=\"submit\" value=\"Submit\"></form>"
				message += "</body></html>"
				self.wfile.write(message)
				print message
				return
			if self.path.endswith("/delete"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				id = self.path.split('/')[2]
				session = DBSession()
				restaurant = session.query(Restaurant).filter_by(id = id).one()
				message = ""
				message += "<html><body>"
				message += "<h1>Delete resturant %s</h1>"% restaurant.name
				message += "<form method='POST' action='/restaurant/%s/delete' enctype='multipart/form-data'>"% (id)
				message += "<input name=\"restaurant_id\" type=\"hidden\" value=\"%s\">"% restaurant.id
				message += "<input type=\"submit\" value=\"Confirm Delete\"></form>"
				message += "</body></html>"
				self.wfile.write(message)
				print message
				return
				
		except IOError:
			self.send_error(404, 'File not found: %s'% self.path)
	def do_POST(self):
		try:
			if self.path.endswith('/hello'):	
				self.send_response(301)
				self.end_headers()

				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields=cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get('message')[0]
				output = ""
				output +=  "<html><body>"
				output += " <h2> Okay, how about this: </h2>"
				output += "<h1> %s </h1>" % messagecontent
				output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
				output += "</html></body>"
				self.wfile.write(output)
				print output
			if self.path.endswith('/restaurant/new'):	
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields=cgi.parse_multipart(self.rfile, pdict)
					name = fields.get('restaurant_name')[0]
				session = DBSession()
				newRestaurant = Restaurant(name = '%s' % name)
				session.add(newRestaurant)
				session.commit()
				print 'DB Entry for %s in Restaurant data base'% name
				self.send_response(301)
				self.send_header('Location', '/restaurant')
				self.end_headers()
			if self.path.endswith("/edit"):
				id = self.path.split('/')[2]
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields=cgi.parse_multipart(self.rfile, pdict)
					name = fields.get('restaurant_name')[0]
				session = DBSession()
				restaurant = session.query(Restaurant).filter_by(id = id).one()
				restaurant.name = name
				session.add(restaurant)
				session.commit()
				self.send_response(301)
				self.send_header('Location', '/restaurant')
				self.end_headers()	
			if self.path.endswith("/delete"):
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields=cgi.parse_multipart(self.rfile, pdict)
					id = fields.get('restaurant_id')[0]
				print 'id is' ,id
				session = DBSession()
				restaurant = session.query(Restaurant).filter_by(id = id).one()
				session.delete(restaurant)
				session.commit()
				self.send_response(301)
				self.send_header('Location', '/restaurant')
				self.end_headers()	
		except:
			pass
def main():
	try:
		port = 8080
		server = HTTPServer(('',port), webServerHandler)
		print "Web server running on port %s"% port
		server.serve_forever()
		

	except KeyboardInterrupt:
		print " ^C entered, stopping web server..."
		server.socket.close()

if __name__=='__main__':
	main()
