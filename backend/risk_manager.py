class RiskManager:
    def __init__(self, daily_target=50.0, risk_per_trade=0.02):
        self.daily_target = daily_target
        self.risk_per_trade = risk_per_trade # Arriesgamos solo el 2% del capital total
        self.min_risk_reward = 1.5 # Buscamos ganar al menos 1.5 veces lo que arriesgamos

    def calculate_position_size(self, balance, entry_price, stop_loss):
        """
        Calcula cuántos contratos comprar basado en la distancia al Stop Loss.
        """
        risk_amount = balance * self.risk_per_trade
        distance_to_sl = abs(entry_price - stop_loss)
        
        if distance_to_sl == 0:
            return 0
            
        # Cantidad de contratos = Dinero a arriesgar / Distancia al SL
        quantity = risk_amount / distance_to_sl
        return round(quantity, 3)

    def get_trade_setup(self, balance, entry_price, side):
        """
        Genera un setup automático con SL y TP basado en volatilidad simple.
        """
        # Por ahora usamos un 1% fijo de SL para la lógica base
        sl_percent = 0.01 
        
        if side == "BUY":
            stop_loss = entry_price * (1 - sl_percent)
            take_profit = entry_price * (1 + (sl_percent * self.min_risk_reward))
        else: # SELL/SHORT
            stop_loss = entry_price * (1 + sl_percent)
            take_profit = entry_price * (1 - (sl_percent * self.min_risk_reward))
            
        qty = self.calculate_position_size(balance, entry_price, stop_loss)
        
        return {
            "side": side,
            "entry": entry_price,
            "sl": stop_loss,
            "tp": take_profit,
            "quantity": qty
        }

if __name__ == "__main__":
    # Simulación de prueba
    rm = RiskManager()
    setup = rm.get_trade_setup(balance=100.0, entry_price=50000.0, side="BUY")
    print(f"--- Simulación AlphaBot-50 ---")
    print(f"Si entramos en {setup['entry']} con $100:")
    print(f"SL: {setup['sl']} | TP: {setup['tp']}")
    print(f"Cantidad de contratos a abrir: {setup['quantity']}")