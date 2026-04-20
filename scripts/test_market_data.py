import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from connection_manager import ConnectionManager
from market_data import MarketDataManager
import json

def test_anomaly_detection():
    print("--- Test: Detección de Anomalías (Whale Spike) ---")
    conn = ConnectionManager()
    mdm = MarketDataManager(conn.get_exchange())
    
    # Obtenemos datos reales
    summary = mdm.get_market_summary()
    
    print(f"Símbolo: {summary['symbol']}")
    print(f"Precio Actual: {summary['price']}")
    print(f"Z-Score de Volumen: {summary['volume_z_score']:.4f}")
    print(f"Detección Ballena: {'🚨 SÍ' if summary['whale_movement'] else '✅ NO'}")
    
    if summary['sentiment']:
        print(f"Sentimiento Top Traders: {summary['sentiment']['bias']} ({summary['sentiment']['ratio']})")
    
    print(f"Listo para Operar: {'🔥 SÍ' if summary['ready_to_trade'] else '⏳ ESPERANDO CONFLUENCIA'}")

if __name__ == "__main__":
    test_anomaly_detection()
