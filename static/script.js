document.addEventListener('DOMContentLoaded', () => {
  const containerNumberInput = document.getElementById('containerNumber');
  const correctedNumberInput = document.getElementById('correctedNumber');
  const copyButton = document.getElementById('copyButton');
  const historyList = document.getElementById('historyList');

  copyButton.disabled = true;

  const validarFormato = (mat) => /^[A-Z]{4}\d{7}$/.test(mat);

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

    copyButton.textContent = "¡Copiado!";
    copyButton.style.background = "#00ffaa";
    setTimeout(() => {
        copyButton.textContent = "Copiar";
        copyButton.style.background = "";
    }, 1200);
  });

  function updateHistoryList(last_corrections, ip_cliente) {
    historyList.innerHTML = '';
    last_corrections.forEach(item => {
      const li = document.createElement('li');
      li.className = 'hist-item';
      li.innerHTML = `
        <span class="hist-mat">${item.corregida}</span>
        <span class="hist-ip${item.ip === ip_cliente ? ' tu' : ''}">${item.ip}${item.ip === ip_cliente ? ' (tú)' : ''}</span>
        <span class="hist-hora">${item.hora_local}</span>
      `;
      historyList.appendChild(li);
    });
  }
});