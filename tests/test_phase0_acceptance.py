"""Criterios de aceptación de la fase 0 (spec §Fases). Quitar el skip al implementar cada uno."""
import pytest

from panspermia import config


def test_obs_dims_match_spec():
    assert config.OBS_DIM == 70
    assert config.N_PRE == 134 and config.N_POST == 69


@pytest.mark.skip(reason="fase 0 pendiente: genome.to_bytes/from_bytes")
def test_genome_roundtrip_10k_mutated():
    """Ida y vuelta sin pérdidas sobre 10^4 genomas mutados; tamaño <= GENOME_MAX_BYTES."""


@pytest.mark.skip(reason="fase 0 pendiente: genome.from_bytes")
def test_genome_rejects_invalid():
    """NaN/Inf, formas erróneas, rangos fuera de límites o hash incoherente => ValueError."""


@pytest.mark.skip(reason="fase 0 pendiente: develop")
def test_develop_deterministic():
    """develop(g) produce el mismo fenotipo bit a bit en ejecuciones repetidas."""


@pytest.mark.skip(reason="fase 0 pendiente: island.epoch")
def test_island_bitwise_determinism_10_epochs():
    """Misma semilla => estado idéntico bit a bit tras 10 épocas."""


@pytest.mark.skip(reason="fase 0 pendiente: ejecución larga, marcar como lenta")
def test_no_extinction_100_epochs_4_of_5_seeds():
    """>= 100 épocas sin extinción en al menos 4 de 5 semillas."""
