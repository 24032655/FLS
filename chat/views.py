from django.shortcuts import render
    
import subprocess
import os

def index(request):
    return render(request, "chat/index.html")
    
def room(request):
    return render(request, 'chat/room.html')
    


def run_script(request):
    if request.method == 'POST':
        # 运行脚本
        process = subprocess.Popen(["python", "your_script.py"])
        # 保存进程ID
        request.session['process_id'] = process.pid
        return HttpResponse("Script started.")
    return render(request, 'your_template.html')

def stop_script(request):
    if request.method == 'POST':
        # 获取进程ID
        process_id = request.session.get('process_id', None)
        if process_id:
            # 终止进程
            os.kill(process_id, signal.SIGTERM)
            del request.session['process_id']
            return HttpResponse("Script stopped.")
        else:
            return HttpResponse("No running script.")
    return render(request, 'your_template.html')


# Create your views here.
