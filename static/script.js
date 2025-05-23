document.addEventListener('DOMContentLoaded', () => {
  const containerNumberInput = document.getElementById('containerNumber');
  const correctedNumberInput = document.getElementById('correctedNumber');
  const copyButton = document.getElementById('copyButton');
  const historyList = document.getElementById('historyList');
  const visitCounter = document.getElementById('visitCounter');

  copyButton.disabled = true;

  let contadorCorregidas = 0;

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

        // Incrementa el contador de corregidas (frontend)
        contadorCorregidas++;
        // Llama al backend para contar también allí
        fetch('/contar_corregida', { method: 'POST' });
      } else {
        correctedNumberInput.classList.remove('valid');
        correctedNumberInput.classList.add('invalid');
        copyButton.disabled = true;
      }

      visitCounter.textContent = data.visits;
    });
  });

  copyButton.addEventListener('click', function() {
    const correctedValue = correctedNumberInput.value;
    if (correctedValue) {
        fetch('/guardar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                corregida: correctedValue,
                hora_local: new Date().toISOString().slice(0, 19).replace('T', ' ')
            })
        });
    }
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

  async function cargarContadores() {
    const res = await fetch('/api/contadores');
    const data = await res.json();
    document.getElementById('corregidasCount').textContent = data.corregidas;
    document.getElementById('copiadasCount').textContent = data.copiadas;
  }
});