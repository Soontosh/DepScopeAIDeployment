from django.http import HttpResponse
from django.template import loader

def live(request):
  """
  Landing page, default template loaded.
  """
  template = loader.get_template('index.html')
  return HttpResponse(template.render())