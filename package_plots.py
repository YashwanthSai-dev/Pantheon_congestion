import zipfile, glob

plot_files = glob.glob("*_throughput.png") + glob.glob("*_loss.png") + glob.glob("*_scatter.png")
zip_path = "pantheon_plots.zip"
with zipfile.ZipFile(zip_path, "w") as zf:
    for f in plot_files:
        zf.write(f)
print(f"Packaged {len(plot_files)} plots into {zip_path}")
