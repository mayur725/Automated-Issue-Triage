async function send(){
  document.getElementById('status').innerText = "Processing...";
  const ticket = {
    ticket_id: document.getElementById('ticket_id').value,
    short_desc: document.getElementById('short_desc').value,
    description: document.getElementById('description').value,
    impact: "user"
  };
  try{
    const resp = await fetch('/triage/single', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(ticket)
    });
    const data = await resp.json();
    document.getElementById('jsonout').innerText = JSON.stringify(data, null, 2);
    document.getElementById('output').style.display = 'block';
    document.getElementById('status').innerText = "Done.";
  }catch(e){
    document.getElementById('status').innerText = "Error: " + e;
  }
}