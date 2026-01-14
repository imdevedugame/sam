#!/bin/bash

# Quick commands for managing the distributed Flask app

case "$1" in
    start)
        echo "🚀 Starting application..."
        systemctl start distributed-flask
        systemctl status distributed-flask --no-pager
        ;;
    
    stop)
        echo "🛑 Stopping application..."
        systemctl stop distributed-flask
        ;;
    
    restart)
        echo "🔄 Restarting application..."
        systemctl restart distributed-flask
        systemctl status distributed-flask --no-pager
        ;;
    
    status)
        echo "📊 Application Status:"
        systemctl status distributed-flask --no-pager
        echo ""
        echo "📊 Nginx Status:"
        systemctl status nginx --no-pager
        ;;
    
    logs)
        echo "📝 Showing real-time logs (Ctrl+C to exit)..."
        journalctl -u distributed-flask -f
        ;;
    
    update)
        echo "📥 Updating application..."
        cd /var/www/sam
        git pull origin main
        source venv/bin/activate
        pip install -r requirements.txt
        deactivate
        systemctl restart distributed-flask
        echo "✅ Update complete!"
        ;;
    
    test)
        echo "🧪 Testing endpoints..."
        echo ""
        echo "1. Testing root endpoint:"
        curl -s http://localhost/ | python3 -m json.tool
        echo ""
        echo "2. Testing health endpoint:"
        curl -s http://localhost/health | python3 -m json.tool
        echo ""
        echo "3. Testing write endpoint:"
        curl -s -X POST http://localhost/write \
          -H "Content-Type: application/json" \
          -d '{"value": 100}' | python3 -m json.tool
        echo ""
        echo "4. Testing read endpoint:"
        curl -s http://localhost/read/node1 | python3 -m json.tool
        ;;
    
    info)
        echo "ℹ️  Application Information:"
        echo ""
        echo "Server IP: $(hostname -I | awk '{print $1}')"
        echo "API URL: http://$(hostname -I | awk '{print $1}')/"
        echo "Dashboard: http://$(hostname -I | awk '{print $1}')/dashboard"
        echo ""
        echo "Service: distributed-flask"
        echo "Location: /var/www/sam"
        echo "Logs: journalctl -u distributed-flask -f"
        echo ""
        ;;
    
    *)
        echo "🛠️  Distributed Flask App Manager"
        echo ""
        echo "Usage: ./manage.sh [command]"
        echo ""
        echo "Commands:"
        echo "  start    - Start the application"
        echo "  stop     - Stop the application"
        echo "  restart  - Restart the application"
        echo "  status   - Show application status"
        echo "  logs     - Show real-time logs"
        echo "  update   - Pull latest code and restart"
        echo "  test     - Test all API endpoints"
        echo "  info     - Show application info"
        echo ""
        echo "Examples:"
        echo "  ./manage.sh start"
        echo "  ./manage.sh logs"
        echo "  ./manage.sh test"
        ;;
esac
