document.addEventListener('DOMContentLoaded', () => {
  const containerNumberInput = document.getElementById('containerNumber');
  const correctedNumberInput = document.getElementById('correctedNumber');
  const copyButton = document.getElementById('copyButton');
  const historyList = document.getElementById('historyList');

  copyButton.disabled = true;

  // Expresión regular para formato válido
  const validarFormato = (mat) => /^[A-Z]{4}\d{7}$/.test(mat);

  // Validación automática al escribir
  containerNumberInput.addEventListener('input', () => {
    const inputValue = containerNumberInput.value;

    fetch('/validar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ matricula: inputValue })
    })
    .then(res => res.json())
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
    });
  });

  // Al pulsar copy se guarda la matrícula validada
  copyButton.addEventListener('click', () => {
  correctedNumberInput.select();
  document.execCommand('copy');

  const horaLocal = new Date().toLocaleString();

  fetch('/guardar', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      corregida: correctedNumberInput.value,
      hora_local: horaLocal
    })
  })
  .then(res => res.json())
  .then(data => {
    updateHistoryList(data.last_corrections, data.ip_cliente);
  })
  .catch(err => console.error('Error al guardar:', err));
});


  function updateHistoryList(corrections, ipCliente) {
    historyList.innerHTML = '';
    corrections.forEach(entry => {
      const isUser = entry.ip === ipCliente;
      const ipHtml = isUser ? `<span class="ip-client">${entry.ip} (tú)</span>` : `<span>${entry.ip}</span>`;
      const li = document.createElement('li');
      li.innerHTML = `<span>${entry.corregida}</span> ${ipHtml} <span style="margin-left: 1rem; font-size: 0.85rem;">🕓 ${entry.hora_local}</span>`;
      historyList.appendChild(li);
    });
  }
});
