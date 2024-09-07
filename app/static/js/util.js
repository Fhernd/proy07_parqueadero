/**
 * Función para formatear un número en dinero.
 * 
 * @param {*} valor Valor a formatear.
 * @param {*} cantidadDigitos Cantidad de dígitos decimales.
 * @returns Valor formateado en dinero.
 */
function formatearDinero(valor, cantidadDigitos) {
    valor = _.ceil(valor, -cantidadDigitos)
    const dineroObjeto = Dinero({ amount: Math.trunc(valor * 100), currency: Dinero.USD });

    const { amount } = dineroObjeto.toJSON();


    return (amount / 100).toLocaleString('es-CO', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}