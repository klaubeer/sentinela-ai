.PHONY: dev parar limpar seed teste migracao shell-bd logs

# Sobe todos os serviços
dev:
	docker-compose up -d
	@echo "\n✅ Sentinela AI rodando:"
	@echo "   API:       http://localhost:8000"
	@echo "   Docs:      http://localhost:8000/docs"
	@echo "   Dashboard: http://localhost:8501"

# Para os serviços
parar:
	docker-compose down

# Remove containers, volumes e dados
limpar:
	docker-compose down -v --remove-orphans

# Roda migrations
migracao:
	docker-compose exec servidor alembic upgrade head

# Popula com dados fake para demo
seed:
	docker-compose exec servidor python -m scripts.popular_dados

# Testes
teste:
	cd servidor && python -m pytest testes/ -v
	cd sdk && python -m pytest testes/ -v

# Abre shell no banco de dados
shell-bd:
	docker-compose exec postgres psql -U sentinela -d sentinela

# Logs em tempo real
logs:
	docker-compose logs -f servidor dashboard
