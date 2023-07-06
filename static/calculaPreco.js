$(document).ready(function() {
    // Function to calculate and update the preco
    function calculaPreco(salgado) {
        var quantidade = parseInt($('#' + salgado).val());
        var preco = 2;  // Default preco for each salgado

        // Calculate the total preco based on the quantidade
        var precoTotal = preco * quantidade;

        // Update the preco in the HTML
        $('#' + salgado + '-preco').text(precoTotal);

        // Recalculate the total price
        var total = 0;
        $('.quantidade').each(function() {
            var salgado = $(this).attr('id');
            var quantidade = parseInt($(this).val());
            total += preco * quantidade;
        });

        // Update the total price in the HTML
        $('#preco-total').text(total);
    }

    // Event listener for quantidade change
    $('.quantidade').on('input', function() {
        var salgado = $(this).attr('id');
        calculaPreco(salgado);
    });
});