document.addEventListener('DOMContentLoaded', () => {
    const containerNumberInput = document.getElementById('containerNumber');
    const correctedNumberInput = document.getElementById('correctedNumber');
    const copyButton = document.getElementById('copyButton');
    const historyList = document.getElementById('historyList');

    // Inicialmente desactivamos el botón
    copyButton.disabled = true;

    const validarFormato = (matricula) => /^[A-Z]{4}\d{7}$/.test(matricula);

    containerNumberInput.addEventListener('input', () => {
        const containerNumber = containerNumberInput.value;

        fetch('/validar', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ matricula: containerNumber })
        })
        .then(response => response.json())
        .then(data => {
            correctedNumberInput.value = data.corregida;
            updateHistoryList(data.last_corrections);

            // Habilitar o deshabilitar el botón según formato válido
            if (validarFormato(data.corregida)) {
                copyButton.disabled = false;
            } else {
                copyButton.disabled = true;
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    copyButton.addEventListener('click', () => {
        correctedNumberInput.select();
        document.execCommand('copy');
    });

    function updateHistoryList(corrections) {
        historyList.innerHTML = '';
        corrections.forEach(correction => {
            const listItem = document.createElement('li');
            listItem.textContent = correction.corregida;
            historyList.appendChild(listItem);
        });
    }
});
