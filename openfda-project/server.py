#!/usr/bin/env python3
#-*- coding: utf-8 -*-


import http.server
import http.client
import json
import socketserver


# Puerto donde funciona
PORT = 8000

# Permitimos reutilizar direcciones
socketserver.TCPServer.allow_reuse_address = True

# Direcciones de la api rest
REST_API_URL = "api.fda.gov"
REST_API_EVENT = "/drug/event.json"
REST_API_LABEL = "/drug/label.json"

#Utilización de clases

class OpenFDAHTML:
    """Clase para la generacion del HTML para la visualizacion
       de la informacion.
    """
    def root_page(self):

        html = """
        <html>
            <head>
                <title>OpenFDA</title>
                <meta charset="UTF-8">
                <meta name="description" content="Proyecto final">
                <meta name="author" content="Gloria Sendra Garcia">
            </head>
            <body>
                <h1>OpenFDA</h1>
                <form method="get" action="listDrugs">
                    <input type= "number" name = "limit" value="10"></input>
                    <input type= "submit" value= "Medicamentos"></input>
                </form>

                <form method="get" action="searchDrug">
                    <input type= "text" name="active_ingredient" value="Drug"> </input>
                    <input type= "number" name="limit" value="10"></input>
                    <input type= "submit" value="Buscar medicamentos"></input>
                </form>

                <form method="get" action="listCompanies">
                    <input type="number" name="limit" value="10"> </input>
                    <input type= "submit" value="Empresas"></input>
                </form>

                <form method="get" action="searchCompany">
                    <input type= "text" name="company" value="company"> </input>
                    <input type= "number" name = "limit" value="10"></input>
                    <input type= "submit" value= "Buscar empresas"></input>
                </form>

                <form method="get" action="listWarnings">
                    <input type="number" name="limit" value="10"> </input>
                    <input type= "submit" value="Advertencias"></input>
                </form>
            </body>
        </html>
        """
        return html

    #Creamos las listas de los medicamentos, las empresas y las advertencias.

    def drugs_list(self, drugs):
        drug_list = ""
        for drug in drugs:
            drug_list += "<li>" + drug + "</li>\n"

        html="""
        <html>
            <head>
                <title>OpenFDA - medicamentos</title>
                <meta charset="UTF-8">
                <meta name="description" content="Proyecto final">
                <meta name="author" content="Gloria Sendra Garcia">
            </head>
                <body>
                    <h1> Medicamentos </h1>
                    <ul>\n""" + drug_list + """</ul>
                </body>
        <html>"""

        return html

    def companies_list(self, companies):

        companies_list = ""

        # Creamos una lista de empresas
        for company in companies:
            companies_list += "<li>" + company + "</li>\n"

        # Generamos la pagina con la lista
        html="""
        <html>
            <head>
                <title>OpenFDA - empresas</title>
                <meta charset="UTF-8">
                <meta name="description" content="Proyecto final">
                <meta name="author" content="Gloria Sendra Garcia">
            </head>
                <body>
                    <h1> Empresas </h1>
                    <ul>\n""" + companies_list + """</ul>
                </body>
        <html>"""
        return html

    def warnings_list(self, warnings):

        warnings_list = ""

        # Creamos una lista de advertencias
        for warning in warnings:
            warnings_list += "<li>" + warning + "</li>\n"

        # Generamos la pagina con la lista
        html="""
        <html>
            <head>
                <title>OpenFDA - advertencias</title>
                <meta charset="UTF-8">
                <meta name="description" content="Proyecto final">
                <meta name="author" content="Gloria Sendra Garcia">
            </head>
                <body>
                    <h1> Advertencias </h1>
                    <ul>\n""" + warnings_list + """</ul>
                </body>
        <html>"""
        return html

    #También vamos a definir el error 404.

    def error404(self):
        html= """
        <html>
            <head>
                <title>OpenFDA - ERROR</title>
                <meta charset="UTF-8">
                <meta name="description" content="Proyecto final">
                <meta name="author" content="Gloria Sendra Garcia">
            </head>
                <body> <h1> ERROR 404 </h1> </body>
        </html>"""
        return html


class OpenFDAClient:
    """Clase con la logica para comunicaciones con la api de fda
    """


    def get_drug(self, drug, limite=10):
        # Obtiene el medicamento especificado buscando por compuesto activo
        conexion = http.client.HTTPSConnection(REST_API_URL)
        conexion.request("GET", REST_API_EVENT + "?search=patient.drug.medicinalproduct:"+drug+"&limit=%s" % str(limite))

        return conexion.getresponse().read().decode("utf8")

    def get_company(self,company, limite=10):
        # Obtiene la empresa buscada
        conexion = http.client.HTTPSConnection(REST_API_URL)
        conexion.request("GET", REST_API_EVENT + "?search="+company+"&limit=%s" % str(limite))

        return conexion.getresponse().read().decode("utf8")

    def get_event(self, limit):
        # Establece limite
        conexion = http.client.HTTPSConnection(REST_API_URL)
        conexion.request("GET", REST_API_EVENT + "?limit=" + limit)

        return conexion.getresponse().read().decode("utf8")

    def get_label(self, limit):
        # Establece limite
        conexion = http.client.HTTPSConnection(REST_API_URL)
        conexion.request("GET", REST_API_LABEL + "?limit=" + limit)

        return conexion.getresponse().read().decode("utf8")


class OpenFDAParser:
    """Clase con la logica para obtener los datos de
    los medicamentos a partir de la respuesta json
    """

    def get_companies(self, info):
        # Parsea las empresas
        loads = json.loads(info)
        companies_list = []

        for load in loads["results"]:
            companies_list += [load["companynumb"]]

        return companies_list


    def get_drugs(self, info):
        # Parsea los medicamentos
        loads = json.loads(info)
        drugs_list = []

        for load in loads["results"]:
            drugs_list += [load["patient"]["drug"][0]["medicinalproduct"]]

        return drugs_list

    def get_warnings(self, info):
        # Parsea las advertencias
        loads = json.loads(info)
        warnings_list = []


        for load in loads["results"]:
            try:
                warnings_list += [load["warnings"][0]]
            except:
                # Algunos medicamentos pueden no tener advertencia y dar keyerror
                warnings_list += ["No warnings"]

        return warnings_list


class OpenFDAHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    """Clase para manejar las peticiones http
       recibidas por el servidor, hace uso de las clases creadas
       OpenFDAClient, OpenFDAHTML y OpenFDAParser
    """

    def do_GET(self):

        # Clase para la conexion con la api rest
        openfdaclient = OpenFDAClient()

        # Clase encargada de parsear la respuesta
        openfdaparser = OpenFDAParser()

        # Clase generadora del html
        openfdahtml = OpenFDAHTML()

        # Inicialmente la respuesta es exitosa
        respuesta = 200

        # Cabeceras de la respuesta
        header1='Content-type'
        header2='text/html'

        # Inicialmente vacio
        html = ""

        if self.path =="/":
            # Devolvemos la pagina principal
            html = openfdahtml.root_page()

        elif "/searchDrug" in self.path:
            if "limit" in self.path:
                drug = self.path.split("=")[1].split("&")[0]
                limit = self.path.split("=")[2]
                events = openfdaclient.get_drug(drug, limit)
            else:
                drug = self.path.split("=")[1]
                events = openfdaclient.get_drug(drug)

            company = openfdaparser.get_companies(events)
            html = openfdahtml.drugs_list(company)

        elif "/searchCompany" in self.path:
            if "limit" in self.path:
                company = self.path.split("=")[1].split("&")[0]
                limit = self.path.split("=")[2]
                events = openfdaclient.get_company(company, limit)
            else:
                company = self.path.split("=")[1]
                events = openfdaclient.get_company(company)

            drugs = openfdaparser.get_drugs(events)
            html= openfdahtml.companies_list(drugs)

        elif "/listDrugs" in self.path:
            limit = self.path.split("=")[1]
            events = openfdaclient.get_event(limit)
            drugs = openfdaparser.get_drugs(events)
            html = openfdahtml.drugs_list(drugs)

        elif "/listCompanies" in self.path:
            limit = self.path.split("=")[1]
            events = openfdaclient.get_event(limit)
            companies = openfdaparser.get_companies(events)
            html = openfdahtml.companies_list(companies)

        elif "/listWarnings" in self.path:
            limit = self.path.split("=")[1]
            events = openfdaclient.get_label(limit)
            warnings = openfdaparser.get_warnings(events)
            html = openfdahtml.warnings_list(warnings)

        elif "/secret" in self.path:
            respuesta = 401
            header1 = "WWW-Authenticate"
            header2 = 'Basic realm="My Realm"'

        elif "/redirect" in self.path:
            respuesta = 302
            header1 = "Location"
            header2 = "http://localhost:8000"

        else:
            # Si no coincide se volverá a la
            # pagina de error con codigo 404
            respuesta = 404
            html= openfdahtml.error404()

        # Escribimos la cabecera de respuesta
        self.send_response(respuesta)
        self.send_header(header1, header2)
        self.end_headers()

        # En caso de exito o de error 404 se envia la pagina html
        if respuesta == 200 or respuesta == 404:
            self.wfile.write(bytes(html,"utf8"))


def server():
    """Lanza el servidor web
    """
    # Creamos el socket TCP con la clase creada
    httpd = socketserver.TCPServer(("", PORT), OpenFDAHTTPRequestHandler)
    print("Servidor funcionando en el puerto %d" % PORT)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor interrumpido desde consola")

    # Cerramos el servidor
    httpd.server_close()


if __name__ == "__main__":

    # Lanzamos el servidor
    server()
