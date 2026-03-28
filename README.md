# Wellness Widget 

## Co to je?
Projekt do školy – server který ti připomíná, 
abys pil vodu, protáhl se a dal si pauzu.
Běží na Ubuntu Serveru ve VirtualBoxu.

## Co jsem použil
- Ubuntu Server 24.04 (VirtualBox)
- Python + Flask (backend)
- Docker (spuštění aplikace)
- Ollama + llama3.2:1b (AI na CPU, bez internetu)
- BIND9 (DNS server)
- isc-dhcp-server (DHCP)
- Python tkinter (desktop widget pro Windows)

## Jak to funguje
1. Server běží ve VirtualBoxu
2. Docker spustí Flask aplikaci na portu 8081
3. Ollama vygeneruje wellness tip (AI)
4. Widget na Windows zobrazí tip vpravo dole
5. Každou hodinu připomene "Napij se vody!" atd.

## Síť
| Co | Hodnota |
|---|---|
| IP serveru | 10.10.10.1 |
| Maska | 255.255.255.0 |
| DHCP rozsah | 10.10.10.100 – 10.10.10.200 |
| DNS | olivieraleszczyk.skola.test |
| Port aplikace | 8081 |

## Jak spustit
### Na Ubuntu serveru:
# Připojení
ssh -p 2222 olik@127.0.0.1

# Spustit vše
sudo systemctl start ollama
sudo systemctl start isc-dhcp-server
sudo systemctl start bind9
cd ~/wellness && sudo docker-compose up -d

### Na Windows (widget):
python widget.py

## Endpointy
- GET /ping → pong
- GET /status → info o serveru
- POST /ai → wellness tip od AI

## Testování
curl http://10.10.10.1:8081/ping
curl http://10.10.10.1:8081/status
curl -X POST http://10.10.10.1:8081/ai

## Ukázkový curl na Ollamu
curl -X POST http://localhost:11434/api/generate \
  -d '{"model":"llama3.2:1b","prompt":"Dej mi wellness tip v cestine.","stream":false}'

## Co nefungovalo a jak jsem to vyřešil
- DHCP nešlo spustit na NAT síti → přidal jsem druhý 
  adaptér (Internal Network) ve VirtualBoxu
- pip3 nefungoval na Ubuntu 24.04 → použil jsem 
  virtual environment (python3 -m venv)
- Docker compose měl starou verzi → použil jsem 
  docker-compose místo docker compose

## Soubory v projektu
- app.py – Flask backend
- index.html – webová stránka s widgetem
- Dockerfile – build Docker image
- docker-compose.yml – spuštění kontejneru
- requirements.txt – Python závislosti
- widget.py – desktop overlay pro Windows
- README.md – tento soubor
