document.addEventListener('DOMContentLoaded', () => {
  const containerNumberInput = document.getElementById('containerNumber');
  const correctedNumberInput = document.getElementById('correctedNumber');
  const copyButton = document.getElementById('copyButton');
  const historyList = document.getElementById('historyList');

  copyButton.disabled = true;

  const validarFormato = (matricula) => /^[A-Z]{4}\d{7}$/.test(matricula);

  containerNumberInput.addEventListener('input', () => {
    const containerNumber = containerNumberInput.value;

    fetch('/validar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ matricula: containerNumber })
    })
    .then(response => response.json())
    .then(data => {
      correctedNumberInput.value = data.corregida;

      if (validarFormato(data.corregida)) {
        correctedNumberInput.classList.add('valid');
        correctedNumberInput.classList.remove('invalid');
        copyButton.disabled = false;
      } else {
        correctedNumberInput.classList.remove('valid');
        correctedNumberInput.classList.add('invalid');
        copyButton.disabled = true;
      }

      updateHistoryList(data.last_corrections, data.ip_cliente);
    })
    .catch(error => {
      console.error('Error:', error);
    });
  });

  copyButton.addEventListener('click', () => {
    correctedNumberInput.select();
    document.execCommand('copy');
  });

  function updateHistoryList(corrections, clientIP) {
    historyList.innerHTML = '';
    corrections.forEach(correction => {
      const listItem = document.createElement('li');
      const ipClass = correction.ip === clientIP ? 'ip-client' : '';
      listItem.innerHTML = `
        <span>${correction.corregida}</span>
        <span class="${ipClass}">${correction.ip === clientIP ? correction.ip + ' (tú)' : correction.ip}</span>
      `;
      historyList.appendChild(listItem);
    });
  }
});
