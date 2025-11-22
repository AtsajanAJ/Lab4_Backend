from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import redis
import os
import time

app = FastAPI()

# Configuration
retries = 10

def get_redis_client():
    """Connect to Redis with retry logic"""
    for i in range(retries):
        try:
            client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'redis'),
                port=6379,
                decode_responses=True
            )
            client.ping()
            print(f"✅ Connected to Redis successfully!")
            return client
        except redis.ConnectionError:
            print(f"⚠️ Redis connection attempt {i+1}/{retries} failed. Retrying...")
            time.sleep(1)
    
    raise Exception("❌ Failed to connect to Redis after multiple retries")

# Initialize Redis client
redis_client = get_redis_client()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Main counter page"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Counter App</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            
            .container {
                text-align: center;
                background: white;
                padding: 60px 80px;
                border-radius: 30px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                animation: fadeIn 0.5s ease-in;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(-20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            h1 {
                color: #333;
                margin-bottom: 20px;
                font-size: 48px;
                font-weight: 700;
            }
            
            #counter {
                font-size: 120px;
                font-weight: bold;
                color: #e74c3c;
                margin: 40px 0;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
                transition: transform 0.2s ease;
            }
            
            #counter.animate {
                transform: scale(1.2);
            }
            
            button {
                background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
                color: white;
                border: none;
                padding: 20px 50px;
                font-size: 24px;
                font-weight: 600;
                border-radius: 50px;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 10px 20px rgba(52, 152, 219, 0.3);
            }
            
            button:hover {
                transform: translateY(-3px);
                box-shadow: 0 15px 30px rgba(52, 152, 219, 0.4);
            }
            
            button:active {
                transform: translateY(-1px);
            }
            
            .footer {
                margin-top: 30px;
                color: #7f8c8d;
                font-size: 14px;
            }
            
            .stats {
                display: flex;
                justify-content: space-around;
                margin-top: 30px;
                padding-top: 30px;
                border-top: 2px solid #ecf0f1;
            }
            
            .stat {
                text-align: center;
            }
            
            .stat-value {
                font-size: 32px;
                font-weight: bold;
                color: #3498db;
            }
            
            .stat-label {
                font-size: 14px;
                color: #7f8c8d;
                margin-top: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Counter</h1>
            <div id="counter">0</div>
            <button onclick="incrementCounter()">Click Me !</button>
            
            <div class="stats">
                <div class="stat">
                    <div class="stat-value" id="total-clicks">0</div>
                    <div class="stat-label">Total Clicks</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="session-clicks">0</div>
                    <div class="stat-label">This Session</div>
                </div>
            </div>
            
            <div class="footer">
                Powered by FastAPI + Redis + Docker
            </div>
        </div>
        
        <script>
            let sessionClicks = 0;
            
            // Load counter on start
            async function loadCounter() {
                try {
                    const response = await fetch('/api/counter');
                    const data = await response.json();
                    document.getElementById('counter').textContent = data.count;
                    document.getElementById('total-clicks').textContent = data.count;
                } catch (error) {
                    console.error('Error loading counter:', error);
                }
            }
            
            // Increment counter
            async function incrementCounter() {
                try {
                    const response = await fetch('/api/increment', {
                        method: 'POST'
                    });
                    const data = await response.json();
                    
                    // Update display
                    const counterElement = document.getElementById('counter');
                    counterElement.textContent = data.count;
                    
                    // Animate
                    counterElement.classList.add('animate');
                    setTimeout(() => {
                        counterElement.classList.remove('animate');
                    }, 200);
                    
                    // Update stats
                    document.getElementById('total-clicks').textContent = data.count;
                    sessionClicks++;
                    document.getElementById('session-clicks').textContent = sessionClicks;
                } catch (error) {
                    console.error('Error incrementing counter:', error);
                    alert('Failed to increment counter. Please try again.');
                }
            }
            
            // Load counter on page load
            loadCounter();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/api/counter")
async def get_counter():
    """Get current counter value from Redis"""
    try:
        count = redis_client.get('counter')
        if count is None:
            redis_client.set('counter', 0)
            count = 0
        return {"count": int(count)}
    except Exception as e:
        return {"error": str(e), "count": 0}

@app.post("/api/increment")
async def increment_counter():
    """Increment counter in Redis"""
    try:
        count = redis_client.incr('counter')
        return {"count": count}
    except Exception as e:
        return {"error": str(e), "count": 0}

@app.get("/current")
async def current():
    """Get current count (alternative endpoint)"""
    try:
        current_count = redis_client.get('counter')
        if current_count is None:
            current_count = 0
        return f'Current number is {current_count}'
    except Exception as e:
        return f'Error: {str(e)}'

@app.get("/health")
async def health():
    """Health check endpoint"""
    try:
        redis_client.ping()
        return {
            "status": "healthy",
            "redis": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "redis": "disconnected",
            "error": str(e)
        }

@app.get("/reset")
async def reset_counter():
    """Reset counter to zero"""
    try:
        redis_client.set('counter', 0)
        return {"message": "Counter reset successfully", "count": 0}
    except Exception as e:
        return {"error": str(e)}

