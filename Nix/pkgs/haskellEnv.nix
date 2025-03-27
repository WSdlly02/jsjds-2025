{
  extraPackages ? [ ],
  haskellPackages,
}:
haskellPackages.ghcWithPackages (
  haskellPackages:
  with haskellPackages;
  [
    fourmolu # Formatter
    # Libs
    JuicyPixels
  ]
  ++ extraPackages
)
