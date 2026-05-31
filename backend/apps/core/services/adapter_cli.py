"""Adapter CLI para motores de generación de horarios

Modo de uso (ejemplo):
  - Función Python local:
      python adapter_cli.py --mode function --module my_engine --callable run_schedule_engine --input DatosBD.xlsx
  - Servicio REST:
      python adapter_cli.py --mode rest --url http://localhost:5000/schedule/run --input DatosBD.xlsx
  - Ejecutable:
      python adapter_cli.py --mode exec --cmd "python my_engine_runner.py --input DatosBD.xlsx --output output.json"

Este script intenta leer `DatosBD.xlsx` usando pandas (si está disponible) y convertirlo a un `input_dict` simplificado.
Si pandas no está instalado, el script imprime instrucciones para generar el JSON de entrada manualmente.

NOTA: Este es solo un ejemplo didáctico. El adaptador real en el backend llamará al motor y persistirá resultados.
"""
import argparse
import json
import subprocess
import sys
import importlib
from pathlib import Path

try:
    import pandas as pd
except Exception:
    pd = None


def read_excel_to_input_dict(path: Path):
    if pd is None:
        raise RuntimeError("pandas no está disponible. Instale con `pip install pandas openpyxl` para usar este CLI")

    xls = pd.read_excel(path, sheet_name=None)
    # Normalizar hojas esperadas: asignatura, docentes, franjas, salones
    def to_records(df_name):
        df = xls.get(df_name, None)
        if df is None:
            return []
        return df.fillna("").to_dict(orient="records")

    return {
        "asignatura": to_records("asignatura"),
        "docentes": to_records("docentes"),
        "franjas": to_records("franjas"),
        "salones": to_records("salones"),
    }


def run_function_mode(module_name, callable_name, input_dict, parameters):
    module = importlib.import_module(module_name)
    func = getattr(module, callable_name)
    result = func(input_dict, parameters)
    return result


def run_rest_mode(url, input_dict, parameters):
    try:
        import requests
    except Exception:
        raise RuntimeError("requests no instalado. Instale con `pip install requests` para usar el modo REST")

    payload = {"input": input_dict, "parameters": parameters}
    resp = requests.post(url, json=payload, timeout=300)
    resp.raise_for_status()
    return resp.json()


def run_exec_mode(cmd, cwd=None):
    completed = subprocess.run(cmd, shell=True, cwd=cwd)
    if completed.returncode != 0:
        raise RuntimeError(f"Comando falló con código {completed.returncode}")
    # Se asume que el ejecutable escribió output.json en el cwd
    out = Path("output.json")
    if not out.exists():
        raise RuntimeError("Se esperaba output.json en el directorio actual pero no existe.")
    return json.loads(out.read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("function", "rest", "exec"), required=True)
    parser.add_argument("--input", help="Path a DatosBD.xlsx")
    parser.add_argument("--module", help="Módulo Python con la función (modo function)")
    parser.add_argument("--callable", help="Nombre de la función a llamar (modo function)")
    parser.add_argument("--url", help="URL del endpoint (modo rest)")
    parser.add_argument("--cmd", help="Comando a ejecutar (modo exec)")
    parser.add_argument("--params", help="JSON con parámetros para el motor", default="{}")
    args = parser.parse_args()

    parameters = json.loads(args.params or "{}")

    input_dict = None
    if args.input:
        path = Path(args.input)
        if not path.exists():
            print(f"Archivo de entrada no encontrado: {path}")
            sys.exit(1)
        try:
            input_dict = read_excel_to_input_dict(path)
        except Exception as exc:
            print("No fue posible leer el Excel:", exc)
            print("Si no desea instalar pandas, puede proporcionar manualmente un JSON de input.")
            sys.exit(1)

    if args.mode == "function":
        if not args.module or not args.callable:
            print("Modo function requiere --module y --callable")
            sys.exit(1)
        result = run_function_mode(args.module, args.callable, input_dict, parameters)
    elif args.mode == "rest":
        if not args.url:
            print("Modo rest requiere --url")
            sys.exit(1)
        result = run_rest_mode(args.url, input_dict, parameters)
    else:
        if not args.cmd:
            print("Modo exec requiere --cmd")
            sys.exit(1)
        result = run_exec_mode(args.cmd)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
