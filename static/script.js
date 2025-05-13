document.addEventListener('DOMContentLoaded', () => {
  const containerNumberInput = document.getElementById('containerNumber');
  const correctedNumberInput = document.getElementById('correctedNumber');
  const copyButton = document.getElementById('copyButton');
  const historyList = document.getElementById('historyList');
  const visitCounter = document.getElementById('visitCounter');

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

      visitCounter.textContent = data.visits;
    });
  });

  copyButton.addEventListener('click', () => {
    correctedNumberInput.select();
    document.execCommand('copy');
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
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>
            ${item.matricula}
            <button onclick="copiarMatricula('${item.matricula}')">Copiar</button>
        </td>
        <td>${item.ip}</td>
        <td>${item.fecha}</td>
      `;
      historyList.appendChild(tr);
    });
  }

  function copiarMatricula(matricula) {
    navigator.clipboard.writeText(matricula);
    // Puedes mostrar un aviso visual si quieres
  }
});