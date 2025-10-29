from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Task
from .serializers import TaskSerializer

@api_view(['GET', 'POST'])
def task_list(request):
    """Handle GET (list tasks) and POST (create task) requests"""
    
    if request.method == 'GET':
        # Filtering
        status_filter = request.GET.get('status')
        priority_filter = request.GET.get('priority')
        
        tasks = Task.objects.all()
        
        if status_filter:
            tasks = tasks.filter(status=status_filter)
        if priority_filter:
            tasks = tasks.filter(priority=priority_filter)
        
        # Sorting
        sort_by = request.GET.get('sort', '-created_at')
        if sort_by in ['due_date', '-due_date', 'priority', '-priority', 'created_at', '-created_at']:
            tasks = tasks.order_by(sort_by)
        
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PATCH', 'DELETE'])
def task_detail(request, id):
    """Handle GET (retrieve), PATCH (update), and DELETE requests for a single task"""
    
    try:
        task = Task.objects.get(id=id)
    except Task.DoesNotExist:
        return Response(
            {'error': 'Task not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = TaskSerializer(task)
        return Response(serializer.data)
    
    elif request.method == 'PATCH':
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def insights(request):
    """Generate smart insights about tasks"""
    
    # Total tasks count
    total_tasks = Task.objects.count()
    
    # Tasks by priority
    priority_stats = Task.objects.values('priority').annotate(
        count=Count('id')
    ).order_by('priority')
    
    # Tasks by status
    status_stats = Task.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Due date analysis
    today = timezone.now().date()
    week_later = today + timedelta(days=7)
    
    due_this_week = Task.objects.filter(
        due_date__gte=today,
        due_date__lte=week_later
    ).exclude(status='done').count()
    
    overdue_tasks = Task.objects.filter(
        due_date__lt=today
    ).exclude(status='done').count()
    
    # Busy day analysis (tasks due by day in the next week)
    busy_days = Task.objects.filter(
        due_date__gte=today,
        due_date__lte=week_later
    ).values('due_date').annotate(
        task_count=Count('id')
    ).order_by('due_date')[:5]
    
    # Priority dominance
    priority_counts = {item['priority']: item['count'] for item in priority_stats}
    dominant_priority = max(priority_counts.items(), key=lambda x: x[1])[0] if priority_counts else None
    
    # Generate summary text
    summary_parts = []
    
    if total_tasks == 0:
        summary_parts.append("No tasks yet. Add some tasks to get started!")
    else:
        if dominant_priority:
            summary_parts.append(f"Your workload is dominated by {dominant_priority} priority tasks.")
        
        if due_this_week > 5:
            summary_parts.append("🚨 Busy week ahead! You have many tasks due this week.")
        elif due_this_week > 2:
            summary_parts.append("📅 Moderate week - you have several tasks coming up.")
        else:
            summary_parts.append("✅ Light week - you're on top of your tasks!")
        
        if overdue_tasks > 0:
            summary_parts.append(f"⚠️ You have {overdue_tasks} overdue task(s) that need attention.")
    
    insights_data = {
        'summary': {
            'text': ' '.join(summary_parts) if summary_parts else "Add tasks to see insights.",
            'total_tasks': total_tasks,
            'due_this_week': due_this_week,
            'overdue_tasks': overdue_tasks,
            'dominant_priority': dominant_priority,
        },
        'priority_breakdown': list(priority_stats),
        'status_breakdown': list(status_stats),
        'busy_days': list(busy_days),
    }
    
    return Response(insights_data)