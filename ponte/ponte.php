<?php
/*
 * PONTE BRASIL do Eldorado (25/10/2026): a mesma ponte do Eldorado0, com os domínios de TODOS os motores do sistema
 * novo (132 domínios registrados, que cobrem os endereços dos motores e os seus subdomínios).
 * Para instalar: substitua public_html/ponte/ponte.php na hospedagem por este arquivo, MANTENDO A SUA CHAVE: copie a
 * linha  const CHAVE = '...';  do arquivo antigo para este (ou deixe a chave na variável de ambiente ELDORADO_PONTE_CHAVE).
 */
/*
 * PONTE BRASIL do Eldorado — lê páginas PÚBLICAS com o IP brasileiro desta hospedagem e devolve ao sistema.
 *
 * Para que serve: alguns portais (TJGO, Câmara e Prefeitura de Goiânia, Diário de Goiás...) recusam endereço
 * estrangeiro. O sistema roda fora do Brasil; esta página, numa hospedagem no Brasil (Hostgator, Locaweb, KingHost...),
 * empresta o endereço brasileiro. Todo o trabalho continua no sistema.
 *
 * Segurança — NÃO é um proxy aberto:
 *   - só aceita pedido assinado com a CHAVE (HMAC-SHA256 de "ts\nurl"), com no máximo 5 minutos de idade;
 *   - só lê os domínios da lista abaixo (sites públicos do catálogo e sufixos públicos do Brasil);
 *   - só https/http, só destino de IP público, no máximo 120 pedidos por minuto e 6 MB por página;
 *   - não guarda nada.
 *
 * Instalação (5 minutos):
 *   1. No painel da hospedagem (Gerenciador de Arquivos), crie a pasta public_html/ponte/ e envie este arquivo.
 *   2. Troque a CHAVE abaixo por uma frase longa e aleatória (40+ caracteres).
 *   3. Nos segredos do sistema, crie dois:
 *        ELDORADO_PONTE_URL   = https://SEU-DOMINIO/ponte/ponte.php
 *        ELDORADO_PONTE_CHAVE = a mesma frase da CHAVE
 *   Pronto: as rodadas dos motores indexadores passam a usar a ponte para os sites que recusam IP estrangeiro.
 *   A lista de domínios é gerada por: python -m src.indexadores ponte-dominios
 */

const CHAVE = 'TROQUE-POR-UMA-FRASE-LONGA-E-ALEATORIA';
const MAX_BYTES = 16000000;   // 03/10: as edições do Diário de Goiânia têm de 8 a 11 MB
const TIMEOUT = 90;
const LIMITE_POR_MINUTO = 120;
// 14/11/2026: o modo do Espião (sites privados fora da lista), com o teto por janela de 6 horas
const TETO_ESPIAO = 300;
const DOMINIOS = [
    'agilicloud.com.br',
    'al.gov.br',
    'alcoa.com',
    'anater.org',
    'ap.gov.br',
    'api-publica.transferegov.gestao.gov.br',
    'atende.net',
    'atosoficiais.com.br',
    'ba.gov.br',
    'banrisulcultural.com.br',
    'baoba.org.br',
    'bnb.gov.br',
    'bndes.gov.br',
    'br.emb-japan.go.jp',
    'br.usembassy.gov',
    'brasil.diplo.de',
    'brazilfoundation.org',
    'bussolasocial.com.br',
    'caixa.gov.br',
    'camara.leg.br',
    'capitaai.com.br',
    'captadores.org.br',
    'captamos.com.br',
    'casa.org.br',
    'ce.gov.br',
    'cese.org.br',
    'cjrfund.org',
    'climaesociedade.org',
    'cnj.jus.br',
    'cnpq.br',
    'congressonacional.leg.br',
    'crcgo.org.br',
    'cultura.gov.br',
    'def.br',
    'df.gov.br',
    'diariomunicipal.com.br',
    'diariooficial.abc.go.gov.br',
    'discricionarias.transferegov.sistema.gov.br',
    'doem.org.br',
    'echoinggreen.org',
    'editais.baoba.org.br',
    'editais.itausocial.org.br',
    'editais.portaldoimpacto.com',
    'editaisculturais.com.br',
    'editaisdobrasil.com',
    'editalong.com',
    'emb-japan.go.jp',
    'es.gov.br',
    'europa.eu',
    'farolcultural.art',
    'fbb.org.br',
    'filantropia.ong',
    'finep.gov.br',
    'fordfoundation.org',
    'funarte.gov.br',
    'funbio.org.br',
    'fundacao.bradesco',
    'fundacaoarcelormittal.org.br',
    'fundacaogrupoboticario.org.br',
    'fundacaoitau.org.br',
    'fundacaotelefonicavivo.org.br',
    'fundacaotidesetubal.org.br',
    'fundacaovale.org',
    'fundobrasil.org.br',
    'fundsforngos.org',
    'gatesfoundation.org',
    'gestao.gov.br',
    'gife.org.br',
    'globalfundforwomen.org',
    'go.equatorialenergia.com.br',
    'go.gov.br',
    'go.leg.br',
    'go.senac.br',
    'goias.gov.br',
    'google.org',
    'gov.br',
    'iadb.org',
    'iaf.gov',
    'idis.org.br',
    'impactarte.org.br',
    'in.gov.br',
    'institutoclaro.org.br',
    'institutococacolabrasil.com.br',
    'institutolocaliza.com.br',
    'institutolojasrenner.org.br',
    'institutonatura.org',
    'institutoneoenergia.org.br',
    'institutosabin.org.br',
    'institutosicoob.org.br',
    'institutounibanco.org.br',
    'institutovotorantim.org.br',
    'ipea.gov.br',
    'itausocial.org.br',
    'jornadasocial.com.br',
    'jpcultura.joaopessoa.pb.gov.br',
    'jus.br',
    'leg.br',
    'mapa.cultura.df.gov.br',
    'mapa.cultura.gov.br',
    'mapa.cultura.rn.gov.br',
    'mapa.cultura.rs.gov.br',
    'mapa.cultura.to.gov.br',
    'mapacultural.al.gov.br',
    'mapacultural.ap.gov.br',
    'mapacultural.ba.gov.br',
    'mapacultural.es.gov.br',
    'mapacultural.fortaleza.ce.gov.br',
    'mapacultural.mg.gov.br',
    'mapacultural.ms.gov.br',
    'mapacultural.pa.gov.br',
    'mapacultural.pb.gov.br',
    'mapacultural.pe.gov.br',
    'mapacultural.se.gov.br',
    'mapacultural.secult.ce.gov.br',
    'mapagoiano.cultura.go.gov.br',
    'mapaosc.ipea.gov.br',
    'mapas.cultura.mt.gov.br',
    'mariaemilia.org.br',
    'mg.gov.br',
    'microsoft.com',
    'movimentobemmaior.org.br',
    'mp.br',
    'mpf.mp.br',
    'mpgo.mp.br',
    'mpt.mp.br',
    'ms.gov.br',
    'mt.gov.br',
    'oakfnd.org',
    'observatorio3setor.org.br',
    'ok.org.br',
    'opensocietyfoundations.org',
    'ovg.org.br',
    'pa.gov.br',
    'pb.gov.br',
    'pe.gov.br',
    'petrobras.com.br',
    'pje.jus.br',
    'pncp.gov.br',
    'portaldoimpacto.com',
    'portaldoincentivo.com.br',
    'pr.gov.br',
    'projudi.tjgo.jus.br',
    'prosas.com.br',
    'redecomua.org.br',
    'rededobem.org.br',
    'rj.gov.br',
    'rn.gov.br',
    'ro.gov.br',
    'rockefellerfoundation.org',
    'rs.gov.br',
    'se.gov.br',
    'sebraego.com.br',
    'senado.leg.br',
    'senaigoias.com.br',
    'sescgo.com.br',
    'sesigoias.com.br',
    'sistema.gov.br',
    'skoll.org',
    'sp.gov.br',
    'spcultura.prefeitura.sp.gov.br',
    'suap.camaragyn.go.gov.br',
    'tjgo.jus.br',
    'to.gov.br',
    'trf1.jus.br',
    'ufg.br',
    'un.org',
    'undp.org',
    'unesco.org',
    'unicef.org',
    'usaid.gov',
    'usembassy.gov',
    'worldbank.org',
    'www.alcoa.com',
    'www.atosoficiais.com.br',
    'www.go.senac.br',
    'www.goiania.go.gov.br',
    'www.goiania.go.leg.br',
    'www.goias.gov.br',
    'www.gov.br',
    'www.mpgo.mp.br',
    'www.portaldoincentivo.com.br',
    'www.sescgo.com.br',
    'www.tjgo.jus.br',
    'www2.fundsforngos.org',
    'www3.sescgo.com.br',
];

header('Content-Type: application/json; charset=utf-8');
header('X-Robots-Tag: noindex');

function sair(array $d, int $codigo = 200): void {
    http_response_code($codigo);
    echo json_encode($d, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

function permitido(string $host): bool {
    $host = strtolower($host);
    foreach (DOMINIOS as $d) {
        if ($host === $d || substr($host, -strlen('.' . $d)) === '.' . $d) {
            return true;
        }
    }
    return false;
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    sair(['ok' => false, 'erro' => 'use POST'], 405);
}
$chave = getenv('ELDORADO_PONTE_CHAVE') ?: CHAVE;
if (strlen($chave) < 24 || strpos($chave, 'TROQUE') === 0) {
    sair(['ok' => false, 'erro' => 'chave da ponte não configurada'], 500);
}
$p = json_decode((string) file_get_contents('php://input'), true);
if (!is_array($p)) {
    sair(['ok' => false, 'erro' => 'pedido inválido'], 400);
}
$url = (string) ($p['url'] ?? '');
$ts = intval($p['ts'] ?? 0);
$assinatura = (string) ($p['assinatura'] ?? '');
if (abs(time() - $ts) > 300) {
    sair(['ok' => false, 'erro' => 'pedido expirado'], 403);
}
$modo = (string) ($p['modo'] ?? '');
$mensagem = $modo === 'espiao' ? $ts . "\n" . $modo . "\n" . $url : $ts . "\n" . $url;   // o modo entra na assinatura
if (!hash_equals(hash_hmac('sha256', $mensagem, $chave), $assinatura)) {
    sair(['ok' => false, 'erro' => 'assinatura inválida'], 403);
}
$u = parse_url($url);
if (!$u || !in_array($u['scheme'] ?? '', ['https', 'http'], true) || empty($u['host'])) {
    sair(['ok' => false, 'erro' => 'endereço inválido'], 400);
}
if ($modo !== 'espiao' && !permitido($u['host'])) {
    sair(['ok' => false, 'erro' => 'dominio fora da lista da ponte: ' . $u['host']], 403);
}
if ($modo === 'espiao') {   // o Espião lê sites privados: no máximo TETO_ESPIAO pedidos a cada 6 horas
    $janela = sys_get_temp_dir() . '/eldorado_ponte_espiao_' . intdiv(time(), 21600);
    $ne = intval(@file_get_contents($janela)) + 1;
    @file_put_contents($janela, (string) $ne);
    if ($ne > TETO_ESPIAO) {
        sair(['ok' => false, 'erro' => 'teto do Espião na janela de 6 horas'], 429);
    }
}
$ip = gethostbyname($u['host']);
if (!filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE)) {
    sair(['ok' => false, 'erro' => 'destino não é público'], 403);
}
$contador = sys_get_temp_dir() . '/eldorado_ponte_' . date('YmdHi');
$n = intval(@file_get_contents($contador)) + 1;
@file_put_contents($contador, (string) $n);
if ($n > LIMITE_POR_MINUTO) {
    sair(['ok' => false, 'erro' => 'limite de pedidos por minuto'], 429);
}
$max = max(1000, min(MAX_BYTES, intval($p['max_bytes'] ?? MAX_BYTES)));
$cab_pedido = [];
foreach ((array) ($p['cabecalhos'] ?? []) as $k => $v) {
    if (in_array(strtolower((string) $k), ['accept', 'accept-language', 'if-none-match', 'if-modified-since'], true)) {
        $cab_pedido[] = $k . ': ' . str_replace(["\r", "\n"], '', (string) $v);
    }
}
$cab_resp = [];
$ch = curl_init($url);
curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_FOLLOWLOCATION => true,
    CURLOPT_MAXREDIRS => 5,
    CURLOPT_TIMEOUT => TIMEOUT,
    CURLOPT_CONNECTTIMEOUT => 15,
    CURLOPT_USERAGENT => 'Mozilla/5.0 (compatible; EldoradoIndexadores/1.0; ponte Brasil)',
    CURLOPT_HTTPHEADER => $cab_pedido,
    CURLOPT_ENCODING => '',
    CURLOPT_PROTOCOLS => CURLPROTO_HTTP | CURLPROTO_HTTPS,
    CURLOPT_REDIR_PROTOCOLS => CURLPROTO_HTTP | CURLPROTO_HTTPS,
    CURLOPT_HEADERFUNCTION => function ($c, $linha) use (&$cab_resp) {
        $i = strpos($linha, ':');
        if ($i !== false) {
            $cab_resp[strtolower(trim(substr($linha, 0, $i)))] = trim(substr($linha, $i + 1));
        }
        return strlen($linha);
    },
    CURLOPT_NOPROGRESS => false,
    CURLOPT_PROGRESSFUNCTION => function ($c, $total, $baixado) use ($max) {
        return ($baixado > $max) ? 1 : 0;
    },
]);
$corpo = curl_exec($ch);
if ($corpo === false) {
    sair(['ok' => false, 'erro' => 'falha de rede na ponte: ' . curl_error($ch)]);
}
$status = intval(curl_getinfo($ch, CURLINFO_RESPONSE_CODE));
$final = (string) curl_getinfo($ch, CURLINFO_EFFECTIVE_URL);
$fu = parse_url($final);
$ipf = ($fu && !empty($fu['host'])) ? gethostbyname($fu['host']) : '';
if (!$fu || empty($fu['host']) || ($modo !== 'espiao' && !permitido($fu['host']))
    || !filter_var($ipf, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE)) {
    sair(['ok' => false, 'erro' => 'redirecionou para domínio fora da lista: ' . ($fu['host'] ?? '?')], 403);
}
$guardar = array_intersect_key($cab_resp, array_flip(['content-type', 'etag', 'last-modified', 'server', 'cf-ray', 'x-wp-totalpages', 'x-wp-total']));
sair(['ok' => true, 'status' => $status, 'url_final' => $final, 'cabecalhos' => $guardar,
      'corpo_b64' => base64_encode(substr((string) $corpo, 0, $max))]);
