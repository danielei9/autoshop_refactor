
#status:

# - Envio de TPV - Maquinas que deben de cobrar
STATUS_TPV_SENT_REQUEST = 7 
# - Maquinas han recibido la orden de pago
STATUS_MACHINES_RECEIVED_REQUEST = 8 
# - Maquinas estan procesando la orden
STATUS_MACHINES_ARE_PROCESSING_REQUEST = 9 
# - Maquinas han finalizado de pagar
STATUS_MACHINES_PAYING_REQUEST_FINISHED = 10
# - Generando ticket
STATUS_MACHINES_PRINTING_TICKET = 11 
#- Orden finalizada
STATUS_MACHINES_ORDER_FINISHED = 12 
#- Orden finalizada
STATUS_MACHINES_ORDER_CANCELLED_OK = 13
#- ha recibido una request de cancelación de la maquina
STATUS_MACHINE_REQUEST_CANCELLED = 2 

#type:

# - ha recibido una request de Pago de la maquina
TYPE_PAY_REQUEST = 0
# - ha recibido una request de configuración de la maquina
TYPE_CONFIG_REQUEST = 1
#- ha recibido una request de cancelación de la maquina
TYPE_CANCELLED_REQUEST = 2 
