# Proyecto - Diseño de lenguajes de programación
### Christopher Sandoval 13660

## Link a video


## Requerimientos
### Graphviz

1. Descargar: https://graphviz.org/download/
2. pip install graphviz

## Ejecución
python main.py <archivo.ATG>
python scanner.py <entrada.txt>

## Funcionamiento del programa
El archivo main.py contiene la implementación del programa. En él se importan métodos de todos los demás archivos para realizar la funcionalidad del programa. Al ejecutar este archivo primero se le solicita al usuario a ingresar una expresión regular. Luego se crea el árbol que describe la estructura de la expresión regular con la función initialize_tree() y separate_children(). Este árbol luego se pasa a la función create_afn() que crea el autómata no determinista por el método de Thompson. Este autómata luego se envía en la función create_afd() y con esto se crea el autómata no determinista por medio del método de subconjuntos. Para realizar el autómata no determinista por medio del método directo primero se debe complementar el arbol creado anteriormente con las propiedades first_pos, last_pos y nullable. Para esto se llama al método find_tree_values() que encuentra recursivamente las propiedades de todos los nodos del árbol. Después con el árbol aumentado se llama al método create_direct_afd() que crea el autómata directo.


El archivo main.py también realiza las simulaciones de los diferentes autómatas. Luego de crear los tres autómatas se le solicita al usuario una cadena para evaluar. Se evalúa esta cadena en los tres autómatas y se muestra al usuario el resultado de la simulación así como los tiempos de ejecución. Luego de mostrar los resultados el usuario puede ingresar otra cadena para simular.

### Creación del árbol inicial
Para crear el árbol se empieza por crear el nodo raíz y se le coloca toda la expresión regular como data. Luego se llama a un método recursivo que analiza el contenido del nodo raíz y empieza la división del contenido entre el hijo izquierdo y derecho. El nodo padre luego se queda con el operando mayor y se llama recursivamente el método de separación para sus dos hijos. Esto se realiza múltiples veces hasta que ya no se puede realizar otra separación.

### Creación del autómata no determinista por Thompson
Para crear el autómata no determinista se toma el árbol creado en el paso anterior. Se inicia en el nodo raíz y se evalúa si sus hijos ya tienen crado un autómata de su operando. Si los hijos no tienen autómata aún se llama el método recursivamente hasta llegar a las hojas. Si los hijos tienen sus autómatas creados entonces se utilizan como los autómatas s y t para el método de Thompson y así ir creando el autómata no determinista completo. Para guardar la información del autómata se crea una nueva instancia de AF y se ingresan todos los estados como instancias de State y transiciones como instancias de Transition.

### Creación del autómata determinista por Subconjuntos
Para crear el autómata determinista se toma el autómata no determinista creado en el paso anterior. Luego se empieza por crear el estado inicial por medio de la cerradura kleen del estado inicial del autómata no determinista. Luego se realiza el proceso de moverse de cada estado con el alfabeto del autómata y realizar la cerradura kleen. Esto genera nuevos estados y transiciones del autómata determinista. Estos nuevos estados tienen como id los sets de estados del autómata no determinista.

### Creación del autómata determinista por método directo
Para crear el autómata determinista por el método directo primero se extiende el árbol que teníamos originalmente. Se llama un método recursivo que recorre todos los nodos para asignarle first_pos, last_pos y nullable. Cuando ya se tiene este árbol aumentado entonces se toma el first_pos del nodo raíz para crear el estado inical del autómata determinista. Luego se calcula el follow_pos de cada symbolo del estado inicial para generar nuevos estados y transiciones. Luego se revisan todos los estados creados para ver cuales contienen el id del symbolo # para establecerlos como estados finales del autómata.

## Clases
### Node
Esta clase se utiliza para crear el árbol que describe la expresión regular. Contiene un método para graficar el autómata con graphviz.

**Parámetros:**
-	id : sirve para identificar cada nodo para poder graficarlos correctamente
-	data: el contenido de este nodo
-	left: contiene la referencia al hijo que tiene este nodo por la izquierda
-	right: contiene la referencia al hijo que tiene este nodo por la derecha
-	parent: contiene la referencia al nodo por encima de este nodo
-	nullable: identifica si el nodo es nullable
-	first_pos: contiene un set con los symbolos del first_pos de este nodo
-	last_pos: contiene un set con los symbolos del last_pos de este nodo
-	symbol_id: el identificador de este nodo si es una hoja

### State
Esta clase describe una clase de un autónomo. Contiene un método que permite la comparación con otras instancias de estado por medio del operador ==.

**Parámetros:**
-	id: el identificador de este estado

### Transition
Esta clase describe una transición de un autómata. Contiene un método que permite la comparación con otras instancias de estado por medio del operador ==.

**Parámetro:**
-	current_state: contiene una referencia al estado actual
-	next_state: contiene una referencia al estado siguiente
-	symbol: es el símbolo de esta transición

### AF
Esta clase describe un autómata finito. Contiene un método para graficar el autómata con graphviz.

**Parámetro:**
-	states: es una lista con todos los estados de este autómata
-	initial_state: contiene una referencia al estado inicial del autómata
-	final_states: contiene una lista con todas las referencias de todos los estados finales
-	transitions: contiene una lista con todas las referencias de todas las transiciones del autómata
-	alphabet: contiene un set con todas las letras del alfabeto del autómata
-	current_node_id: es una variable que se utiliza 
