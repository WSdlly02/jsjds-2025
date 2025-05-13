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
    haskell-language-server
  ]
  ++ extraPackages
)
