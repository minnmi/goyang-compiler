# Goyang Language


### Características

- Linguagem de programação estruturada.
- Fortemente tipada.
- Arquitetura x86.
- Compatível com o compilador FASM.


### Exemplo de código
``` python
begin
    int numero;
    int fatorial;

    write("Escreva um numero");
    read(numero);

    fatorial:=1;
    while(numero > 1):
        fatorial := fatorial * numero;
        numero := numero - 1;
    end
    write("fatorial");
end

```

### Output
