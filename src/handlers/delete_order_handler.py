"""
Handler: delete order
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
import config
import requests
from handlers.handler import Handler
from order_saga_state import OrderSagaState

class DeleteOrderHandler(Handler):
    """ Handle order deletion during rollback. """

    def __init__(self, order_id):
        """ Constructor method """
        self.order_id = order_id
        super().__init__()

    def run(self):
        """Call StoreManager to delete order"""
        try:
            response = requests.delete(f'{config.API_GATEWAY_URL}/store-manager-api/orders/{self.order_id}')
            if response.ok:
                self.logger.debug(f"Transition d'état: DeleteOrder -> ORDER_DELETED")
                return OrderSagaState.ORDER_DELETED
            else:
                self.logger.error(f"DeleteOrder a échoué : {response.status_code}")
                return OrderSagaState.END

        except Exception as e:
            self.logger.error(f"DeleteOrder a échoué : {str(e)}")
            return OrderSagaState.END
        
    def rollback(self):
        """
        (rollback not applicable for DeleteOrder)
        """
        pass
