from django import forms
from .models import *
from django.contrib import messages
from django.shortcuts import render, redirect

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = "__all__"

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = "__all__"

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ["cliente"]

class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ["producto", "cantidad"]

INDICATIVOS = [
    ('+57', '+57 (Colombia)'),
    # Agrega los que necesites
]

class ClienteForm(forms.ModelForm):
    indicativo = forms.ChoiceField(
        choices=INDICATIVOS,
        label='Indicativo',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    celular_numero = forms.CharField(
        label='Celular',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de celular'}),
        max_length=10
    )

    class Meta:
        model = Cliente
        fields = ['nombre', 'documento', 'correo', 'direccion', 'tipo', 'notas']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
            'documento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de documento'}),

            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Notas adicionales'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Si ya existe un número, separarlo en dos partes
        if self.instance and self.instance.celular:
            for indicativo, _ in INDICATIVOS:
                if self.instance.celular.startswith(indicativo):
                    self.fields['indicativo'].initial = indicativo
                    self.fields['celular_numero'].initial = self.instance.celular[len(indicativo):]
                    break

    def clean(self):
        cleaned_data = super().clean()
        indicativo = cleaned_data.get("indicativo")
        celular_numero = cleaned_data.get("celular_numero")

        if indicativo and celular_numero:
            cleaned_data['celular'] = f"{indicativo}{celular_numero}"
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.celular = self.cleaned_data.get('celular')
        if commit:
            instance.save()
        return instance

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'documento', 'correo', 'celular', 'tipo', 'notas']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo'
            }),
            'documento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Documento de identidad'
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Correo electrónico'
            }),
            'celular': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de celular'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales sobre el cliente'
            }),
        }