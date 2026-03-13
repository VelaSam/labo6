"""
Handler: create payment transaction
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
import config
import requests
from handlers.handler import Handler
from order_saga_state import OrderSagaState

class CreatePaymentHandler(Handler):
    """ Handle the creation of a payment transaction for a given order. Trigger rollback of previous steps in case of failure. """

    def __init__(self, order_id, order_data):
        """ Constructor method """
        self.order_id = order_id
        self.order_data = order_data
        self.total_amount = 0
        super().__init__()

    def run(self):
        """Call payment microservice to generate payment transaction"""
        try:
            response_order = requests.get(f'{config.API_GATEWAY_URL}/store-manager-api/orders/{self.order_id}')
            if not response_order.ok:
                self.logger.error(f"Erreur lors de la récupération de la commande {self.order_id}")
                return self.rollback()
            
            order_details = response_order.json()
            self.total_amount = order_details.get('total_amount', 0)

            response_payment = requests.post(f'{config.API_GATEWAY_URL}/payments-api/payments',
                json={
                    "order_id": self.order_id,
                    "user_id": self.order_data.get('user_id'),
                    "total_amount": self.total_amount
                },
                headers={'Content-Type': 'application/json'}
            )

            if response_payment.ok:
                self.logger.debug("Transition d'état: CreatePayment -> PAYMENT_CREATED")
                return OrderSagaState.PAYMENT_CREATED
            else:
                self.logger.error(f"CreatePayment a échoué : {response_payment.status_code}")
                return self.rollback()

        except Exception as e:
            self.logger.error(f"CreatePayment a échoué : {str(e)}")
            return self.rollback()
        
    def rollback(self):
        """ Call StoreManager to restore stock quantities if payment transaction creation fails """
        try:
            response = requests.put(f'{config.API_GATEWAY_URL}/store-manager-api/stocks',
                json={
                    "items": self.order_data.get('items', []),
                    "operation": "+"
                },
                headers={'Content-Type': 'application/json'}
            )
            if response.ok:
                self.logger.debug("Transition d'état: CreatePaymentFailure -> STOCK_INCREASED")
                return OrderSagaState.STOCK_INCREASED
            else:
                self.logger.error("Erreur lors de la restauration du stock")
                return OrderSagaState.END
        except Exception as e:
            self.logger.error(f"Erreur lors de la restauration du stock: {str(e)}")
            return OrderSagaState.END
