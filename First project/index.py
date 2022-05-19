from cgitb import text
from tkinter import ttk
from tkinter import *

import sqlite3
from turtle import width

class Product:

    #9. GUARDAMOS EL NOMBRE DE NUESTRA BASE DE DATOS
    db_name = "database.db"

    #10. CREAMOS UNA FUNCION PARA HACER LA CONEXION CON DB CADA VEZ QUE QUERAMOS HACER ALGO
    def run_query(self, query, parameters = ()):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor() #PERMITE OBTENER DESDE QUE POSICION ESTOY EN LA DB
            resultado = cursor.execute(query, parameters) #DEFINIMOS LA CONSULTA SQL CON .execute
            conn.commit() #EJECUTAMOS LO QUE DEFINIMOS ANTERIORMENTE CON .commit
        return resultado

    #11. CREAMOS UNA FUNCION PARA TRAER TODOS LOS DATOS DE LA DB
    def get_productos(self):
        #LIMPIAMOS LA TABLA
        items = self.tree.get_children() #.get_children ES PARA OBTENER TODOS LOS DATOS DE LA TABLA
        for elemento in items:
            self.tree.delete(elemento)
        #CONSULTANDO LOS DATOS DE LA DB
        query = "SELECT * FROM productos ORDER BY id DESC"
        db_datos = self.run_query(query)
        for fila in db_datos:
            self.tree.insert("", 0, text=fila[0], values=(fila[1], fila[2], fila[3]))  

    #13. AGREGAMOS UNA FUNCION PARA VALIDAR QUE LOS DATOS NO ESTEN VACIOS
    def validacion(self):
        return len(self.name.get()) != 0 and len(self.price.get()) and len(self.amount.get())

    #14. YA CON LA VALIDACION, DAMOS FUNCIONALIDAD AL BOTON
    def agregar_productos(self):
        if self.validacion():
            query = "INSERT INTO productos VALUES(NULL, ?, ?, ?)"
            parametros = (self.name.get(), self.price.get(), self.amount.get())
            self.run_query(query, parametros)
            self.message["text"] = "El producto {} fue agregado exitosamente".format(self.name.get())
            self.name.delete(0,END) #PARA VOLVERLO A SU ESTADO INICIAL
            self.price.delete(0,END)
            self.amount.delete(0,END)
        else:
            self.message["text"] = "Por favor, ingresar los valores completos"
        self.get_productos()

    #16. AGREGAMOS EL BOTON PARA ELIMINAR EL PRODUCTO SELECCIONADO, PARA ELLO CREAMOS SU BOTON
    def eliminar_producto(self):
        self.message["text"] = ""
        try:
            self.tree.item(self.tree.selection())["values"][0]
        except IndexError as e:
            self.message["fg"] = "red"
            self.message["text"] = "Por favor, seleccionar un item"
            return
        self.message["text"] = ""
        nombre = self.tree.item(self.tree.selection())["values"][0]
        query = "DELETE FROM productos WHERE nombre = ?"
        parametros = (nombre)
        self.run_query(query, (parametros, ))
        self.message["text"] = "El item seleccionado: {} a sido eliminado correctamente".format(nombre)
        self.get_productos()

    #17. CREAMOS LA FUNCION DE EDITAR
    def editar_producto(self):
        self.message["text"] = ""
        try:
            self.tree.item(self.tree.selection())["values"][0]
        except IndexError as e:
            self.message["fg"] = "red"
            self.message["text"] = "Por favor, seleccionar un item"
            return
        name_old = self.tree.item(self.tree.selection())["values"][0]
        price_old = self.tree.item(self.tree.selection())["values"][1]
        amount_old = self.tree.item(self.tree.selection())["values"][2]
        #17.1. CREAMOS UNA VENTANA PARA EDITAR, CON Toplevel()
        self.editar_wind = Toplevel()
        self.editar_wind.title("Editar producto")
        #CREAMOS UN LABEL PARA QUE SE VEAN LOS DATOS ANTERIORES
        Label(self.editar_wind, text="Nombre anterio: ").grid(row=0, column=1)
        Entry(self.editar_wind, textvariable=StringVar(self.editar_wind, value=name_old), state="readonly").grid(row=0,column=2)
        #CREAMOS EL LABEL INPUT DEL NUEVO VALOR
        Label(self.editar_wind, text="Nuevo nombre: ").grid(row=1, column=1)
        new_name = Entry(self.editar_wind)
        new_name.grid(row=1, column=2)
        #AHORA EL PRECIO
        Label(self.editar_wind, text="Precio anterior: ").grid(row=2, column=1)
        Entry(self.editar_wind, textvariable=StringVar(self.editar_wind, value=price_old), state="readonly").grid(row=2, column=2)
        Label(self.editar_wind, text="Nuevo precio: ").grid(row=3, column=1)
        new_price = Entry(self.editar_wind)
        new_price.grid(row=3, column=2)
        #PARA AMOUNT
        Label(self.editar_wind, text="Cantidad anterior: ").grid(row=4, column=1)
        Entry(self.editar_wind, textvariable=StringVar(self.editar_wind, value=amount_old), state="readonly").grid(row=4, column=2)
        new_amount = Entry(self.editar_wind)
        new_amount.grid(row=5, column=2)
        Label(self.editar_wind, text="Cantidad actual :").grid(row=5, column=1)
    
        #18. CREAMOS EL BOTON DENTRO DE NUESTRA NUEVA VENTANA
        Button(self.editar_wind, text="Update", command=lambda: self.editar_item(new_name.get(), name_old, new_price.get(), price_old, new_amount.get(), amount_old)).grid(row=7, column=2, sticky=W)

    #19. CREAMOS LA FUNCION EDITAR DE LA NUEVA VENTANA   
    def editar_item(self, new_name, name_old, new_price, price_old, new_amount, amount_old):
        query = "UPDATE productos SET nombre = ?, precio = ?, cantidad = ? WHERE nombre = ? AND precio = ? AND cantidad = ?"
        parametros = (new_name, new_price, new_amount, name_old, price_old, amount_old)
        self.run_query(query,parametros)
        self.editar_wind.destroy()
        self.message["text"] = "El item {} fue actualizado exitosamente".format(name_old)
        self.get_productos()

    #21. CREAMOS LA FUNCION PARA REALIZAR UNA VENTA
    def realizar_compra(self):
        self.solicitud_wind = Toplevel()
        self.solicitud_wind.title("Solicitud de compra")
        #GUARDAMOS LOS VALORES DE NUESTRA DB
        self.valores_db_enlistados = []
        self.productos_db = []
        self.precios_db = []
        self.stock_db = []
        for line in self.tree.get_children():
            for value in self.tree.item(line)['values']:
                self.valores_db_enlistados.append(value)
        for i in range(0, len(self.valores_db_enlistados), 3):
            self.productos_db.append(self.valores_db_enlistados[i])
            self.precios_db.append(self.valores_db_enlistados[i+1])
            self.stock_db.append(self.valores_db_enlistados[i+2])
        #CREAMOS EL MARCO DE CONSULTA
        self.frame_consulta = LabelFrame(self.solicitud_wind, text="Consulta")
        self.frame_consulta.grid(row=0, column=0, columnspan=4, pady=10, padx=10)
        #CREAMOS EL INPUT PARA QUE INGRESE EL ITEM A CONSULTAR
        Label(self.frame_consulta, text="Ingresar nombre:", width=18).grid(row=1, column=0)
        # self.name_consultado = Entry(self.frame_consulta)
        self.name_consultado = ttk.Combobox(self.frame_consulta, state="readonly", width=20)
        self.name_consultado.grid(row=1, column=1)
        self.name_consultado["values"] = self.productos_db
        self.name_consultado.current(0)
        #CREAMOS EL BOTON PARA BUSCAR
        ttk.Button(self.frame_consulta, text="Buscar", command=self.realizar_consulta).grid(row=1, column=3)
        Label(self.frame_consulta, text="Precio unitario S/.", width=18).grid(row=2, column=0)
        Entry(self.frame_consulta, textvariable=StringVar(self.solicitud_wind), state="readonly", width=23).grid(row=2,column=1)
        Label(self.frame_consulta, text="Cantidad en stock", width=18).grid(row=3, column=0)
        Entry(self.frame_consulta, textvariable=StringVar(self.solicitud_wind), state="readonly", width=23).grid(row=3,column=1)
        
        #CREAREMOS UN MARCO PARA REALIZAR EL PEDIDO
        self.monto_acumulado = 0
        self.frame_pedido = LabelFrame(self.solicitud_wind, text="Realizar pedido")
        self.frame_pedido.grid(row=5, column=0, pady=10, padx=10)
        Label(self.frame_pedido, text="Nombre").grid(row=6, column=0)
        self.name_pedido = Entry(self.frame_pedido)
        self.name_pedido.grid(row=6, column=1)
        Label(self.frame_pedido, text="Cantidad").grid(row=7, column=0)
        self.cantidad_pedido = Entry(self.frame_pedido)
        self.cantidad_pedido.grid(row=7, column=1)
        ttk.Button(self.frame_pedido, text="Agregar al carrito", command=self.agregar_carrito).grid(row=8, column=0, columnspan=2, sticky=W+E)
        Label(self.frame_pedido, text="Monto acumulado").grid(row=10, column=0)
        Entry(self.frame_pedido, textvariable=StringVar(self.solicitud_wind, value=self.monto_acumulado), state="readonly").grid(row=10,column=1)
        self.message_pedido = Label(self.frame_pedido, text="", fg="green")
        self.message_pedido.grid(row=9, column=0, columnspan=2, sticky=W+E)

        #CREAMOS UN MARCO PARA LA CONFIRMACION DEL PEDIDO
        self.producto_acumulado = []
        self.cantidades_acumuladas = []
        self.frame_confirmacion = LabelFrame(self.solicitud_wind, text="Confirmacion de pedido", width=200)
        self.frame_confirmacion.grid(row=5, column=2, columnspan=2, pady=10, padx=10)
        
        ttk.Button(self.frame_confirmacion, text="Modificar pedido", command=self.modificar_carrito).grid(row=8, column=2, sticky=W+E)
        ttk.Button(self.frame_confirmacion, text="Limpiar pedido", command = self.limpiar_pedido).grid(row=8, column=3, sticky=W+E)
        ttk.Button(self.frame_confirmacion, text="Confirmar compra", command=self.realizar_venta).grid(row=9, column=2, columnspan=2, sticky=W+E)
        self.message_acumulado = Label(self.frame_confirmacion, text="", fg="green")
        self.message_acumulado.grid(row=10, column=2, columnspan=2, sticky=W+E)

        self.tree_carrito = ttk.Treeview(self.solicitud_wind, height=10, columns=("col1", "col2"))
        self.tree_carrito.grid(row=11, column=0, columnspan=2, pady=20, padx=20)
        self.tree_carrito.column("#0", width=180)
        self.tree_carrito.column("#1", width=80, anchor=CENTER)
        self.tree_carrito.column("#2", width=80, anchor=CENTER)
        self.tree_carrito.heading("#0", text="Nombre", anchor=CENTER)
        self.tree_carrito.heading("#1", text="Precio (S/.)", anchor=CENTER)
        self.tree_carrito.heading("#2", text="Cantidad", anchor=CENTER)

    #22. DEEFINIMOS LA FUNCION PARA REALIZAR LA CONSULTA
    def realizar_consulta(self):
        self.get_productos()
        #GUARDAMOS EL NOMBRE INGRESADO
        nombre_consultado = self.name_consultado.get()
        #MODIFICAMOS EL VALOR DE LAS ENTRADAS
        nega = 0
        for i in range(len(self.valores_db_enlistados)):
            if self.valores_db_enlistados[i] == nombre_consultado:
                Entry(self.frame_consulta, textvariable=StringVar(self.solicitud_wind, value=self.valores_db_enlistados[i+1]), state="readonly").grid(row=2,column=1)
                Entry(self.frame_consulta, textvariable=StringVar(self.solicitud_wind, value=self.valores_db_enlistados[i+2]), state="readonly").grid(row=3,column=1)
            else:
                nega +=1
        if nega == len(self.valores_db_enlistados):
            Entry(self.frame_consulta, textvariable=StringVar(self.solicitud_wind, value=""), state="readonly").grid(row=2,column=1)
            Entry(self.frame_consulta, textvariable=StringVar(self.solicitud_wind, value=""), state="readonly").grid(row=3,column=1)

    #23. CREAMOS LA FUNCION PARA AGREGAR AL CARRITO
    def agregar_carrito(self):
        if len(self.name_pedido.get()) != 0 and len(self.cantidad_pedido.get()) != 0:
            self.get_productos()
            nombre_pedido = str(self.name_pedido.get())
            cantidad_pedida = int(self.cantidad_pedido.get())
            valores_enlistados_low = []
            # for i in range(len(valores_enlistados)):
            #     valor = str(valores_enlistados[i])
            #     if valor.lower() == nombre_pedido.lower():
            #         precio_item = float(valores_enlistados[i+1])
            #         cantidad_stock = int(valores_enlistados[i+2])
            #         self.tree_carrito.insert("", 0, text=nombre_pedido.capitalize(), values=(precio_item, cantidad_stock))
            #     else:
            #         nega +=1
            for valor in self.valores_db_enlistados:
                indice_valor = self.valores_db_enlistados.index(valor)
                strValor = str(valor)
                valores_enlistados_low.append(strValor.lower())
                if strValor.lower() == nombre_pedido.lower():
                    precio_item = float(self.valores_db_enlistados[indice_valor+1])
                    cantidad_stock = int(self.valores_db_enlistados[indice_valor+2])
                    if cantidad_stock>=cantidad_pedida:
                        self.tree_carrito.insert("", 0, text=nombre_pedido.capitalize(), values=(precio_item, cantidad_pedida))
                        self.message_pedido["text"] = "El producto: {} fue agregado correctamente".format(nombre_pedido)
                    else:
                        self.message_pedido["fg"] = "red"
                        self.message_pedido["text"] = "No contamos con la cantidad solicitada"
                        precio_item = 0
                        cantidad_pedida = 0
                        self.name_pedido.delete(0,END) 
                        self.cantidad_pedido.delete(0,END)
            if nombre_pedido not in valores_enlistados_low:
                self.message_pedido["text"] = "Por favor corriga el nombre"
                self.message_pedido["fg"] = "red"
                precio_item = 0
                cantidad_pedida = 0    
            # if nega == len(valores_enlistados):
            #     self.message_pedido["text"] = "Por favor volver a ingresar un nombre"
            #     self.message_pedido["fg"] = "red"
            #     precio_item = 0
            #     cantidad_pedida = 0
            # elif cantidad_pedida > cantidad_stock:
            #     self.message_pedido["fg"] = "red"
            #     self.message_pedido["text"] = "No contamos con la cantidad solicitada"
            #     precio_item = 0
            #     cantidad_pedida = 0
            #     self.name_pedido.delete(0,END) 
            #     self.cantidad_pedido.delete(0,END)
            # else:
            #     self.message_pedido["text"] = "El producto: {} fue agregado correctamente".format(nombre_pedido)
            self.monto_acumulado = self.monto_acumulado + precio_item*cantidad_pedida
            self.producto_acumulado.append(nombre_pedido.capitalize())
            self.cantidades_acumuladas.append(cantidad_pedida)
            if self.producto_acumulado[-1] == 0 or self.cantidades_acumuladas[-1] == 0:
                self.producto_acumulado.remove(self.producto_acumulado[-1])
                self.cantidades_acumuladas.remove(self.cantidades_acumuladas[-1])
            Entry(self.frame_pedido, textvariable=StringVar(self.solicitud_wind, value=self.monto_acumulado), state="readonly").grid(row=10,column=1)
            
            self.name_pedido.delete(0,END) 
            self.cantidad_pedido.delete(0,END)
        else:
            self.message_pedido["text"] = "Por favor, ingresar los valores completos"
            self.message_pedido["fg"] = "red"
            
    #24. CREAMOS LA FUNCION DE CONFIRMACION DE VENTA
    def realizar_venta(self):
        if len(self.producto_acumulado) != 0:
            par_producto_cantidad = {}
            par_db = {}
            #CREAMOS LOS DICCIONARIOS EN FUNCION DEL PRODUCTO Y CANTIDAD
            for x in range(len(self.producto_acumulado)):
                par_producto_cantidad[self.producto_acumulado[x]] = self.cantidades_acumuladas[x]
            for y in range(len(self.productos_db)):
                par_db[self.productos_db[y]] = self.stock_db[y]
            #RELLENAMOS LOS VALORES DE LOS OTROS ITEMS CON 0
            for item in self.productos_db:
                if item not in self.producto_acumulado:
                    par_producto_cantidad[item] = 0
            #ACTUALIZAMOS LOS ITEMS ACTUALES DESPUES DE LA VENTA 
            par_stock_actualizado = {}
            for producto in par_db:
                par_stock_actualizado[producto] = par_db[producto] - par_producto_cantidad[producto]
                #REALIZAREMOS UN QUERY QUE ACTUALIZE LA CANTIDAD DE CADA ITEM EN FUNCION DEL ULTIMO DICCIONARIO DE STOCK ACTUALIZADO
                name = producto
                new_amount = par_stock_actualizado[producto]
                query = "UPDATE productos SET cantidad = ? WHERE nombre = ?"
                parametros = (new_amount, name)
                self.run_query(query,parametros)
            self.message_acumulado["text"] = "Venta exitosa, por favor cobrar: S/.{}".format(self.monto_acumulado)
            self.productos_db = []
            self.cantidades_db = []
            self.limpiar_pedido()
            self.get_productos()
        else:
            self.message_acumulado["fg"] = "red"
            self.message_acumulado["text"] = "Por favor ingresar pedido"
        self.get_productos()
        
    #25. CREAMOS LA FUNCION DE LIMPIAR PARA DESPUES QUE CONFIRMAR LA VENTA
    def limpiar_pedido(self):
        self.name_pedido.delete(0,END) 
        self.cantidad_pedido.delete(0,END)
        self.monto_acumulado = 0
        self.producto_acumulado = []
        self.cantidades_acumuladas = []
        Entry(self.frame_pedido, textvariable=StringVar(self.solicitud_wind, value=self.monto_acumulado), state="readonly").grid(row=10,column=1)
        self.message_pedido["text"] = ""
        self.message_acumulado["text"] = ""
        for line in self.tree_carrito.get_children():
            self.tree_carrito.delete(line)
        self.get_productos()
            
    #26. CREAMOS LA FUNCION QUE EDITARA NUESTRO CARRITO
    def modificar_carrito(self):
        self.message_acumulado["text"] = ""
        try:
            self.tree_carrito.item(self.tree_carrito.selection())["values"][0]
        except IndexError as e:
            self.message_acumulado["fg"] = "red"
            self.message_acumulado["text"] = "Por favor, seleccionar item"
            return
        self.name_modificar = self.tree_carrito.item(self.tree_carrito.selection())["text"]
        self.precio_modi = self.tree_carrito.item(self.tree_carrito.selection())["values"][0]
        amount_old = self.tree_carrito.item(self.tree_carrito.selection())["values"][1]
        #17.1. CREAMOS UNA VENTANA PARA EDITAR, CON Toplevel()
        self.mod_carrito_wind = Toplevel()
        self.mod_carrito_wind.title("Modificar cantidad")
        Label(self.mod_carrito_wind, text="Nombre: ").grid(row=0, column=1)
        Entry(self.mod_carrito_wind, textvariable=StringVar(self.mod_carrito_wind, value=self.name_modificar), state="readonly").grid(row=0,column=2)
        Label(self.mod_carrito_wind, text="Precio: ").grid(row=1, column=1)
        Entry(self.mod_carrito_wind, textvariable=StringVar(self.mod_carrito_wind, value=self.precio_modi), state="readonly").grid(row=1,column=2)
        Label(self.mod_carrito_wind, text="Cantidad actual: ").grid(row=2, column=1)
        Entry(self.mod_carrito_wind, textvariable=StringVar(self.mod_carrito_wind, value=amount_old), state="readonly").grid(row=2, column=2)
        self.new_amount_modi = Entry(self.mod_carrito_wind)
        self.new_amount_modi.grid(row=3, column=2)
        Label(self.mod_carrito_wind, text="Nueva cantidad:").grid(row=3, column=1)
        Button(self.mod_carrito_wind, text="Update", command=self.editar_carrito_item).grid(row=5, column=2, sticky=W)
        self.message_modificar_cantidad = Label(self.mod_carrito_wind, text="", fg="red")
        self.message_modificar_cantidad.grid(row=6, column=1, columnspan=2, sticky=W+E)
    #27. CREAMOS LA FUNCION QUE HARA EL BOTON DE MODIFICAR EL CARRITO
    def editar_carrito_item(self):
        indice_nombre_modificar = self.valores_db_enlistados.index(self.name_modificar) 
        stock = int(self.valores_db_enlistados[indice_nombre_modificar+2])
        if stock >= int(self.new_amount_modi.get()):
            self.tree_carrito.item(self.tree_carrito.selection(), values = (self.precio_modi, int(self.new_amount_modi.get())))
            self.mod_carrito_wind.destroy()
            valores_tree = []
            acumulado = 0
            for line in self.tree_carrito.get_children():
                for value in self.tree_carrito.item(line)['values']:
                    valores_tree.append(value)
            for i in range(0, len(valores_tree), 2):
                precio = float(valores_tree[i])
                cantidad = int(valores_tree[i+1])
                acumulado += precio*cantidad
            Entry(self.frame_pedido, textvariable=StringVar(self.solicitud_wind, value=acumulado), state="readonly").grid(row=10,column=1)
            self.message_pedido["text"] = ""
        else:
            self.message_modificar_cantidad["text"] = "No contamos con stock suficiente"
        
            
    #2. DEFINIMOS UN CONSTRUCTOR QUE TOMARA SELF Y EL WINDOW QUE LE ESTAMOS PASANDO
    def __init__(self, window):
        #3. wind SERA PARA ALMACENAR MI VENTANA QUE ME ESTAN PASANDO COMO PARAMETRO 
        self.wind = window
        self.wind.title("Tiendita Don Pepe")    
        
        #4. CREAMOS UN FRAME (CONTENEDOR)
        frame = LabelFrame(self.wind, text=" Registre un nuevo producto: ")
        frame.grid(row=0, column=0, columnspan=4, pady=(10, 0))

        #5. CREAMOS UNA ENTRADA (INPUT)
        Label(frame, text="Nombre: ", width=10).grid(row=1, column=0)
        self.name = Entry(frame) #CON Entry creamos un input
        self.name.focus() #PONEMOS EL CURSOR AQUI
        self.name.grid(row=1, column=1)

        #6. CREAMOS LAS SIGUIENTES ENTRADAS:
        Label(frame, text="Precio unitario: ", width=12).grid(row=2, column=0)
        self.price = Entry(frame) #CON Entry creamos un input
        self.price.grid(row=2, column=1)

        Label(frame, text="Cantidad: ", width=10).grid(row=3, column=0)
        self.amount = Entry(frame) #CON Entry creamos un input
        self.amount.grid(row=3, column=1)

        #7. CREAMOS LOS BOTONES PARA AGREGAR (con sticky definimos el ancho)
        #14.1. AGREGAMOS EL COMANDO command Y AGREGAMOS LA FUNCION QUE CREAMOS
        ttk.Button(frame, text="Registrar producto", command=self.agregar_productos).grid(row=4, column = 0, sticky=W+E)
        #20. CREAMOS EL BOTON PARA REALIZAR EL PEDIDO
        ttk.Button(frame, text="Realizar compra", command=self.realizar_compra).grid(row=4, column=1, sticky=W+E)

        #15. MENSAJE DE ESTADO
        self.message = Label(text="", fg="green")
        self.message.grid(row=5, column=0, columnspan=2, sticky=W+E)

        #8. CREAMOS UNA TABLA
        self.tree = ttk.Treeview(height=20, columns=("col1", "col2", "col3"))
        self.tree.grid(row=6, column=0, columnspan=2, padx=30)
        self.tree.column("#0", width=40)
        self.tree.column("#1", width=150)
        self.tree.column("#2", width=100, anchor=CENTER)
        self.tree.column("#3", width=80, anchor=CENTER)
        self.tree.heading("#0", text="N°", anchor=CENTER)
        self.tree.heading("#1", text="Nombre", anchor=CENTER)
        self.tree.heading("#2", text="Precio (S/.)", anchor=CENTER)
        self.tree.heading("#3", text="Cantidad", anchor=CENTER)

        #16.1. CREAMOS EL BOTON PARA ELIMINAR Y EDITAR
        ttk.Button(text="Eliminar", command=self.eliminar_producto).grid(row=7, column=0, sticky=W+E)
        ttk.Button(text="Editar", command=self.editar_producto).grid(row=7, column=1, sticky=W+E)
        
        #12. LLAMAMOS LA FUNCION .get_productos A PENAS NUESTRA APLICACION INICIA
        self.get_productos()

#1. ANTES DE COMENZAR, DEBEMOS COMPROBAR SI ESTE ES EL ARCHIVO MAIN    
if __name__ == '__main__':
    window = Tk()
    application = Product(window)
    window.mainloop()