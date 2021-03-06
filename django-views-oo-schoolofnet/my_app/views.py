from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View, RedirectView, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.views.generic.edit import FormMixin
from .models import Address
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django import forms
from django.core.mail import send_mail
from .forms import AddressForm
from .choices import STATE_CHOICES


class LoginView(TemplateView):
    template_name = 'my_app/login.html'
    tipo = 'Padrão'

    def get(self, request, *args, **kwargs):
        return self.render_to_response({'tipo': self.tipo})

    def post(self, request, *args, **kwargs):
        context = {
            'app_path': request.get_full_path
        }
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            # print(vars(user))
            django_login(request, user)

            # Redireciona caso haja next
            next_param = request.GET.get('next')
            if next_param:
                return redirect(next_param)
            return redirect('/home/')

        context['message'] = 'Dados inválidos'
        return self.render_to_response(context)


# class LoginView(View):
#     template_name = 'my_app/login.html'
#     tipo = 'Padrão'
#
#     def get(self, request, *args, **kwargs):
#         context = {
#             'app_path': request.get_full_path,
#             'tipo': self.tipo
#         }
#         return render(request, self.template_name, context)
#
#     def post(self, request, *args, **kwargs):
#         context = {
#             'app_path': request.get_full_path
#         }
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#
#         user = authenticate(username=username, password=password)
#
#         if user is not None:
#             # print(vars(user))
#             django_login(request, user)
#
#             # Redireciona caso haja next
#             next_param = request.GET.get('next')
#             if next_param:
#                 return redirect(next_param)
#             return redirect('/home/')
#
#         context['message'] = 'Dados inválidos'
#         return render(request, self.template_name, context)


# 301 - permanente (browser salva como cache destino)
# 302 - temporário
class LogoutRedirectView(RedirectView):
    url = '/login/'

    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    def get(self, request, *args, **kwargs):
        django_logout(request)
        return super().get(request, *args, **kwargs)


# protegendo da maneira *2
# @method_decorator(login_required(login_url='/login/'), name='dispatch')
class TesteView(LoginRequiredMixin, TemplateView):
    # protegendo da maneira *3 (LoginRequiredMixin)
    template_name = 'my_app/home.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response({})

    # protegendo da maneira *1
    # @method_decorator(login_required(login_url='/login/'))
    # def dispatch(self, request, *args, **kwargs):
    #     return super().dispatch(request, *args, **kwargs)


@login_required(login_url='/login/')
def logout(request):
    django_logout(request)
    return redirect('/login/')


def login(request):
    context = {
        'app_path': request.get_full_path
    }
    if request.method == 'GET':
        return render(request, 'my_app/login.html', context)
    username = request.POST.get('username')
    password = request.POST.get('password')

    user = authenticate(username=username, password=password)

    if user is not None:
        # print(vars(user))
        django_login(request, user)

        # Redireciona caso haja next
        next_param = request.GET.get('next')
        if next_param:
            return redirect(next_param)
        return redirect('/home/')

    context['message'] = 'Dados inválidos'
    return render(request, 'my_app/login.html', context)


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'my_app/home.html'

# @login_required(login_url='/login/')
# def home(request):
#     return render(request, 'my_app/home.html')


# Ver MultipleObjectMixin
class AdressListView(LoginRequiredMixin, ListView):
    model = Address
    template_name = 'my_app/address/list.html'
    # paginate_by = 1
    # context_object_name = 'addresses'

# @login_required(login_url='/login/')
# def address_list(request):
#     addresses = Address.objects.all()
#     context = {
#         'addresses': addresses
#     }
#     return render(request, 'my_app/address/list.html', context)


# Criação sem utilização do form orientado a objeto
# @login_required(login_url='/login/')
# def address_create(request):
#     if request.method == 'GET':
#         context = {
#             'states': STATE_CHOICES
#         }
#         return render(request, 'my_app/address/create.html', context)
#
#     # Post --> salvar
#     Address.objects.create(
#         address=request.POST.get('address'),
#         address_complement=request.POST.get('address_complement'),
#         city=request.POST.get('city'),
#         state=request.POST.get('state'),
#         country=request.POST.get('country'),
#         user=request.user
#     )
#
#     return redirect('/addresses/')

# Form orientado a objetos
# @login_required(login_url='/login/')
# def address_create(request):
#     form_submitted = False
#     if request.method == 'GET':
#         form = AddressForm()
#     else:
#         form_submitted = True
#         form = AddressForm(request.POST)
#         if form.is_valid():
#             Address.objects.create(
#                 address=form.cleaned_data['address'],
#                 address_complement=form.cleaned_data['address_complement'],
#                 city=form.cleaned_data['city'],
#                 state=form.cleaned_data['state'],
#                 country=form.cleaned_data['country'],
#                 user=request.user
#             )
#             return redirect('/addresses/')
#
#     return render(request, 'my_app/address/create.html', {'form': form, 'form_submitted': form_submitted})


# Ver SingleObjectMixin
class AddressDetail(LoginRequiredMixin, DetailView):
    model = Address
    template_name = 'my_app/address/detail.html'


class FormSubmittedToContext(FormMixin):
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form, form_submitted=True))


class AddressCreate(LoginRequiredMixin, FormSubmittedToContext, CreateView):
    model = Address
    form_class = AddressForm
    template_name = 'my_app/address/create.html'
    # fields = ['address', 'address_complement', 'city', 'state', 'country']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    # validação sem FormSubmittedToContext
    # def form_invalid(self, form):
    #     return self.render_to_response(self.get_context_data(form=form, form_submitted=True))


# Form utilizando Model
@login_required(login_url='/login/')
def address_create(request):
    form_submitted = False
    if request.method == 'GET':
        form = AddressForm()
    else:
        form_submitted = True
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('my_app:address_list')

    return render(request, 'my_app/address/create.html', {'form': form, 'form_submitted': form_submitted})


# -------------------- update ---------------------
# Form não orientado a objeto
# @login_required(login_url='/login/')
# def address_update(request, id):
#     address = Address.objects.get(id=id)
#     if request.method == 'GET':
#         context = {
#             'states': STATE_CHOICES,
#             'address': address
#         }
#         return render(request, 'my_app/address/update.html', context)
#
#     # Post --> atualizar
#     address.address = request.POST.get('address')
#     address.address_complement = request.POST.get('address_complement')
#     address.city = request.POST.get('city')
#     address.state = request.POST.get('state')
#     address.country = request.POST.get('country')
#     address.save()
#
#     return redirect('/addresses/')

# Form orientado a objeto
# @login_required(login_url='/login/')
# def address_update(request, id):
#     form_submitted = False
#     address = Address.objects.get(id=id)
#     if request.method == 'GET':
#         form = AddressForm(address.__dict__)
#     else:
#         form_submitted = True
#         form = AddressForm(request.POST)
#         if form.is_valid():
#             address.address = form.cleaned_data['address']
#             address.address_complement = form.cleaned_data['address_complement']
#             address.city = form.cleaned_data['city']
#             address.state = form.cleaned_data['state']
#             address.country = form.cleaned_data['country']
#             address.save()
#
#             return redirect('/addresses/')
#     return render(request, 'my_app/address/update.html',
#                   {'address': address, 'form': form, 'form_submitted': form_submitted})


class AddressUpdate(LoginRequiredMixin, FormSubmittedToContext, UpdateView):
    model = Address
    form_class = AddressForm
    template_name = 'my_app/address/update.html'
    success_url = reverse_lazy('my_app:address_list')


# Form utilizando Model
@login_required(login_url='/login/')
def address_update(request, id):
    form_submitted = False
    address = Address.objects.get(id=id)
    if request.method == 'GET':
        form = AddressForm(instance=address)
    else:
        form_submitted = True
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            address.save()
            return redirect('my_app:address_list')
    return render(request, 'my_app/address/update.html',
                  {'address': address, 'form': form, 'form_submitted': form_submitted})


class AddressDeleteView(LoginRequiredMixin, DeleteView):
    model = Address
    template_name = 'my_app/address/destroy.html'
    success_url = reverse_lazy('my_app:address_list')


@login_required(login_url='/login/')
def address_destroy(request, id):
    address = Address.objects.get(id=id)
    if request.method == 'GET':
        form = AddressForm(instance=address)
    else:
        address.delete()
        return redirect('my_app:address_list')

    context = {
        'address': address,
        'form': form
    }
    return render(request, 'my_app/address/destroy.html', context)


class ContactForm(forms.Form):
    name = forms.CharField(
        label='Seu nome',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='Seu e-mail',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    subject = forms.CharField(
        label='Assunto',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))

    def send_mail(self):
        #subject = '%s - %s' % (self.cleaned_data['name'], self.cleaned_data['subject'])

        send_mail(
            self.cleaned_data['subject'],
            self.cleaned_data['message'],
            self.cleaned_data['email'],
            [settings.EMAIL_TO],
            fail_silently=False,
        )


class ContactView(FormView):
    template_name = 'my_app/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('my_app:contact')

    def form_valid(self, form):
        form.send_mail()
        # print(form.cleaned_data['name'])
        return super().form_valid(form)


