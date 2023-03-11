import { embeddingView, fsView, heatmap } from './store.mjs';

let title,
    method,
    data,
    id = 0;

async function ensembleDR() {
    title = d3.select('#dataTitle').property('value');
    method = d3.select('#method').property('value');
    await d3
        .json(`/v2/preset?title=${title}&method=${method}`)
        .then((response) => {
            console.log(response);
            data = response;
            data.embedding.forEach((e) => {
                embeddingView.add(
                    id++,
                    e.method,
                    e.hyperparameter,
                    e.embedding
                );
            });
        });
}

export { ensembleDR };
