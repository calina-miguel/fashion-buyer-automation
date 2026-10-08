import fs from 'node:fs';

const path = 'fashion-buyer-interest-workflow.json';
const workflow = JSON.parse(fs.readFileSync(path, 'utf8'));

for (const node of workflow.nodes) {
  if (node.type === 'n8n-nodes-base.googleSheets') {
    node.parameters.documentId.value = '1JJeV-0lKKblJNfrygcIPKhJDqV8kUCl28F1pj1AiV04';
    node.parameters.sheetName.value = 'Sheet1';
  }

  if (node.name === 'Alert Sales Team') {
    node.parameters.sendTo = 'calina.miguel@gmail.com';
  }

  for (const key of ['message', 'subject', 'responseBody']) {
    if (typeof node.parameters[key] !== 'string') continue;
    node.parameters[key] = node.parameters[key]
      .replaceAll('{{ $env.LOOKBOOK_LINK }}', 'https://github.com/calina-miguel/fashion-buyer-automation')
      .replaceAll('{{ $env.SHOPPING_ASSIST_LINK }}', 'https://www.instagram.com/p/DeILJlkALF6/?stkn=YmhnNzBpMzMxNzA1')
      .replaceAll("{{ $env.STORE_NAME || 'The Store Team' }}", 'Luma & Thread');
  }
}

fs.writeFileSync(path, `${JSON.stringify(workflow, null, 2)}\n`);
